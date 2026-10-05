"""Build the clean USA Rev 1 alpha. Retail identity validation is mandatory."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, pathlib, shutil, struct, subprocess, sys, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
CODE_HASH='ef210566e1d9d16879a746dfb063fcbad232f0171d860de906531ecc526cc020'
def digest(data):return hashlib.sha256(data).hexdigest()
def run(args):subprocess.run([str(x) for x in args],check=True,cwd=ROOT)
def read_elf(path):
    data=path.read_bytes()
    if data[:7]!=b'\x7fELF\x01\x01\x01':raise ValueError('Expected little-endian ELF32')
    machine=struct.unpack_from('<H',data,18)[0]
    if machine!=40:raise ValueError('Expected ARM ELF')
    off=struct.unpack_from('<I',data,32)[0];size,count,names=struct.unpack_from('<HHH',data,46)
    sections=[struct.unpack_from('<10I',data,off+i*size) for i in range(count)]
    ns=sections[names];strings=data[ns[4]:ns[4]+ns[5]]
    output=[]
    for s in sections:
        name=strings[s[0]:].split(b'\0',1)[0].decode()
        if s[5] and s[2]&2:
            if s[1] not in (1,8):raise ValueError(f'Unsupported allocated section {name}: {s[1]}')
            blob=bytes(s[5]) if s[1]==8 else data[s[4]:s[4]+s[5]]
            output.append((name,s[3],blob))
    return sorted(output,key=lambda s:s[1])
def generate(version,patches):
    dest=ROOT/'source/generated';dest.mkdir(exist_ok=True)
    (dest/'version.h').write_text(f'#pragma once\n#define TOS_VERSION "{version}"\n')
    layouts=json.loads((ROOT/'config/layout.json').read_text())['groups']
    anchors={'top_left':'ANCHOR_TOP_LEFT','top_right':'ANCHOR_TOP_RIGHT','bottom_right':'ANCHOR_BOTTOM_RIGHT','center':'ANCHOR_CENTER'}
    lines=['#pragma once','#include "../render/layout.h"']
    for name,l in layouts.items():
        lines.append('static const Layout TOS_'+name.upper()+'={'+','.join([anchors[l['anchor']],*[f'{float(l.get(k,0))}f' for k in ['x','y','scale','width','height']]])+'};')
    (dest/'layout.h').write_text('\n'.join(lines)+'\n')
    glyphs=json.loads((ROOT/'config/glyphs.json').read_text())
    (dest/'glyphs.h').write_text('#pragma once\n#include "../render/layout.h"\ntypedef enum {'+','.join('GLYPH_'+g for g in glyphs)+'} Glyph;\nstatic const Rect tosGlyphs[]={'+','.join('{'+','.join(str(v) for v in vals)+'}' for vals in glyphs.values())+'};\n')
    asm=['.syntax unified','.arm']
    ld=['OUTPUT_FORMAT("elf32-littlearm")','OUTPUT_ARCH(arm)','ENTRY(tos_before)','SECTIONS {']
    for p in sorted(patches,key=lambda p:int(p['address'],16)):
        name='.patch_'+p['name'];asm.extend([f'.section {name},"ax",%progbits',p['assembly']]);ld.append(f' {name} {p["address"]} : {{ KEEP(*({name})) }}')
    ld.extend([' . = 0x00610000;',' .payload : { *(.text*) *(.rodata*) *(.data*) }',' .zero : { *(.bss*) *(COMMON) }',' /DISCARD/ : { *(.comment*) *(.note*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }','}'])
    (dest/'patches.s').write_text('\n'.join(asm)+'\n');(dest/'linker.ld').write_text('\n'.join(ld)+'\n')
def load_module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def validate_retail(code,patches):
    if digest(code)!=CODE_HASH:raise ValueError('Retail code SHA-256 mismatch; refusing to build')
    previous=0
    for p in sorted(patches,key=lambda p:int(p['address'],16)):
        a=int(p['address'],16);o=a-0x100000;expected=bytes.fromhex(p['expected'])
        if len(expected)!=p['size']:raise ValueError('Incomplete expected bytes: '+p['name'])
        if a<previous:raise ValueError('Overlapping declaration: '+p['name'])
        if code[o:o+len(expected)]!=expected:raise ValueError('Original bytes mismatch: '+p['name'])
        previous=a+len(expected)
def resources(retail,romfs):
    inputs=json.loads((ROOT/'config/resource_inputs.json').read_text())
    if romfs:
        with zipfile.ZipFile(romfs) as z:
            for path,info in inputs.items():
                data=z.read(path)
                if digest(data)!=info['sha256']:raise ValueError('Pristine resource mismatch: '+path)
                (retail/info['file']).write_bytes(data)
    for path,info in inputs.items():
        if digest((retail/info['file']).read_bytes())!=info['sha256']:raise ValueError('Resource identity mismatch: '+path)
    output=ROOT/'load/mods/0004000000033500/romfs';previews=ROOT/'docs/previews'
    load_module('build_hud_atlas').build(retail/'hud_all00_base.ctxb',ROOT/'assets',output/'menu/01_US_ENGLISH/hud_all00.ctxb',previews/'hud_atlas.png')
    load_module('build_menu_top_atlas').build(retail/'menu_top_parts00_base.ctxb',ROOT/'assets',output/'menu/01_US_ENGLISH/menu_top_parts00.ctxb',previews/'menu_atlas.png')
    load_module('build_ocarina_atlas').build(retail/'menu_okarina_parts00_base.ctxb',output/'menu/01_US_ENGLISH/menu_okarina_parts00.ctxb',previews/'ocarina_atlas.png')
    load_module('build_message_parts_atlas').build(retail/'message_parts_base.ctxb',output/'message/parts.ctxb',previews/'message_atlas.png')
    load_module('build_frontend_atlases').build(retail,output/'menu/01_US_ENGLISH',previews)
    # Preserve the proven alpha-098 menu cursor resource. It participates in
    # the native menu presentation path and is intentionally copied verbatim.
    cursor=ROOT/'assets/menu_cursor00_alpha098.ctxb'
    if digest(cursor.read_bytes())!='bbdc4d88b6d42e7951085659489e38b40e0c6dc616a793c1112830e36c2995d8':
        raise ValueError('Historical menu_cursor00 identity mismatch')
    shutil.copyfile(cursor,output/'menu/01_US_ENGLISH/menu_cursor00.ctxb')
    # Assert XY identity in both native Ocarina texture families. This fails if
    # a copied historical builder accidentally reintroduces a semantic swap.
    for name,base,target,rects in [
        ('build_ocarina_atlas','menu_okarina_parts00_base.ctxb',output/'menu/01_US_ENGLISH/menu_okarina_parts00.ctxb',[(176,160,192,176),(192,160,208,176)]),
        ('build_message_parts_atlas','message_parts_base.ctxb',output/'message/parts.ctxb',[(32,48,48,64),(48,48,64,64)])]:
        m=load_module(name);before=m.decode_ctxb((retail/base).read_bytes());after=m.decode_ctxb(target.read_bytes())
        for rect in rects:
            if before.crop(rect).tobytes()!=after.crop(rect).tobytes():raise ValueError('Ocarina XY glyph changed unexpectedly')
def make_ips(sections,patches):
    declared={'.patch_'+p['name']:p for p in patches};manifest=[];ips=bytearray(b'PATCH');previous=0
    for name,a,blob in sections:
        if a<previous:raise ValueError('Overlapping ELF output '+name)
        previous=a+len(blob)
        if name in declared:
            p=declared.pop(name)
            if a!=int(p['address'],16) or len(blob)!=p['size']:raise ValueError('Patch extent mismatch '+name)
        elif name not in ('.payload','.zero'):raise ValueError('Unexpected allocated section '+name)
        if name in ('.payload','.zero') and (a<0x610000 or a+len(blob)>0x700000):raise ValueError('Payload exceeds declared allocation budget')
        manifest.append(dict(section=name,address=hex(a),size=len(blob),sha256=digest(blob)))
        for start in range(0,len(blob),65535):
            chunk=blob[start:start+65535];offset=a+start-0x100000
            if offset==0x454F46 or offset<0 or offset>0xFFFFFF:raise ValueError('Invalid IPS offset')
            ips.extend(offset.to_bytes(3,'big')+len(chunk).to_bytes(2,'big')+chunk)
    if declared:raise ValueError('Missing ELF patches: '+','.join(declared))
    ips.extend(b'EOF');return bytes(ips),manifest
def package(version,output):
    names=[]
    for p in ROOT.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if any(part in ('.build','__pycache__','.git') for part in rel.parts):continue
        if p.suffix in ('.zip','.pyc','.o','.exe','.elf','.ttf','.otf','.woff','.woff2'):continue
        names.append((rel.as_posix(),p))
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,p in sorted(names):
            info=zipfile.ZipInfo(name,(2026,10,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16;z.writestr(info,p.read_bytes())
    return names
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--retail-dir',type=pathlib.Path,required=True);parser.add_argument('--romfs',type=pathlib.Path)
    parser.add_argument('--zig',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True)
    args=parser.parse_args();args.retail_dir=args.retail_dir.resolve();args.zig=args.zig.resolve();args.output=args.output.resolve()
    v=json.loads((ROOT/'VERSION.json').read_text())
    if set(v)!=set(['major','milestone','iteration']) or any(type(x)!=int or x<0 for x in v.values()):raise ValueError('Invalid independent counters')
    version='.'.join(str(v[k]) for k in ['major','milestone','iteration'])
    if args.output.name!=f'tos-alpha-{version}.zip':raise ValueError('Output name must match version counters')
    patches=json.loads((ROOT/'config/patches.json').read_text());code=(args.retail_dir/'code.bin').read_bytes();validate_retail(code,patches);generate(version,patches)
    build=ROOT/'.build';build.mkdir(exist_ok=True)
    common=[args.zig,'cc','-target','arm-freestanding-eabi','-mcpu=arm1176jzf_s','-marm','-mfpu=vfpv2','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-ffunction-sections','-fdata-sections']
    objects=[]
    for p in sorted((ROOT/'source').rglob('*')):
        if p.suffix not in ('.c','.s'):continue
        obj=build/('_'.join(p.relative_to(ROOT/'source').parts)+'.o');run(common+['-c',p,'-o',obj]);objects.append(obj)
    elf=build/'tos.elf'
    run(common+['-nostdlib','-Wl,-e,tos_before','-Wl,--gc-sections','-Wl,--no-undefined','-Wl,-T,'+str(ROOT/'source/generated/linker.ld'),*objects,'-o',elf])
    sections=read_elf(elf);ips,manifest=make_ips(sections,patches)
    dest=ROOT/'load/mods/0004000000033500';(dest/'exefs').mkdir(parents=True,exist_ok=True)
    (dest/'exefs/code.ips').write_bytes(ips)
    exheader=bytearray((ROOT/'assets/exheader.bin').read_bytes())
    if len(exheader) not in (0x400,0x800):raise ValueError('Unexpected exheader extent')
    address,maxPages,textSize=struct.unpack_from('<III',exheader,0x10)
    roAddr,roPages,roSize=struct.unpack_from('<III',exheader,0x20)
    dataAddr,dataPages,dataSize=struct.unpack_from('<III',exheader,0x30)
    oldBss=struct.unpack_from('<I',exheader,0x3C)[0]
    nativeEnd=dataAddr+dataPages*0x1000+((oldBss+0xFFF)&~0xFFF)
    end=max(a+len(b) for _,a,b in sections)
    if address!=0x100000 or roAddr!=address+maxPages*0x1000 or dataAddr!=roAddr+roPages*0x1000:raise ValueError('Noncontiguous retail allocation')
    if nativeEnd>0x610000:raise ValueError('Payload overlaps retail BSS')
    newBss=((end+0xFFF)&~0xFFF)-(dataAddr+dataPages*0x1000)
    struct.pack_into('<I',exheader,0x3C,max(oldBss,newBss))
    (dest/'exheader.bin').write_bytes(exheader)
    resources(args.retail_dir,args.romfs.resolve() if args.romfs else None)
    runtime='NOT_RUN'
    runtime_path=ROOT/'docs/RUNTIME_SMOKE.json'
    if runtime_path.exists():
        smoke=json.loads(runtime_path.read_text())
        if smoke.get('ips_sha256')==digest(ips):runtime=smoke['result']
    report=dict(version=version,counters=v,retail_sha256=digest(code),patch_count=len(patches),ips_sha256=digest(ips),native_allocation_end=hex(nativeEnd),payload_start='0x610000',payload_end=hex(end),bss_size=hex(max(oldBss,newBss)),sections=manifest,runtime_validation=runtime,frontend_replay='EXACT_PRODUCER_PASS_SCOPED_VISUAL_ACCEPTANCE_PENDING')
    (ROOT/'docs/BUILD_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
    files={p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in ROOT.rglob('*') if p.is_file() and '.build' not in p.parts and '__pycache__' not in p.parts and p.name!='CHECKSUMS.json' and p.suffix.lower() not in ('.ttf','.otf','.woff','.woff2')}
    (ROOT/'docs/CHECKSUMS.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
    args.output.parent.mkdir(parents=True,exist_ok=True);names=package(version,args.output)
    print(json.dumps(dict(zip=str(args.output),version=version,entries=len(names),bytes=args.output.stat().st_size,patches=len(patches),sha256=digest(args.output.read_bytes()))))
if __name__=='__main__':main()
