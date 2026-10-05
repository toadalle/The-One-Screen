"""Independently compare CCI ExeFS code against the supplied decompressed code."""
import argparse, hashlib, json, pathlib, struct, zipfile

def compare_romfs(f,base,archive):
    f.seek(base);header=struct.unpack('<10I',f.read(40))
    if header[0]!=40:raise ValueError('RomFS table header')
    f.seek(base+header[3]);dirs=f.read(header[4])
    f.seek(base+header[7]);files=f.read(header[8])
    entries={};visited=set()
    def walk(offset,parent):
        if offset in visited:raise ValueError('RomFS directory cycle')
        visited.add(offset)
        _,sibling,child,first,_,length=struct.unpack_from('<6I',dirs,offset)
        name=dirs[offset+24:offset+24+length].decode('utf-16le')
        path=parent+name+'/' if name else parent
        n=first;seen=set()
        while n!=0xffffffff:
            if n in seen:raise ValueError('RomFS file cycle')
            seen.add(n)
            _,nextfile,data,size,_,length=struct.unpack_from('<IIQQII',files,n)
            name=files[n+32:n+32+length].decode('utf-16le')
            entries[path+name]=(base+header[9]+data,size);n=nextfile
        n=child
        while n!=0xffffffff:
            walk(n,path);n=struct.unpack_from('<I',dirs,n+4)[0]
    walk(0,'')
    with zipfile.ZipFile(archive) as z:
        zipped={n for n in z.namelist() if not n.endswith('/')}
        if set(entries)!=zipped:raise ValueError('RomFS file list mismatch')
        for path,(offset,size) in entries.items():
            f.seek(offset);data=f.read(size)
            if data!=z.read(path):raise ValueError('RomFS data mismatch: '+path)
    return len(entries)

def decompress(data):
    descriptor, added = struct.unpack_from('<II', data, len(data)-8)
    output = bytearray(len(data)+added)
    output[:len(data)] = data
    index = len(data)-(descriptor>>24)
    stop = len(data)-(descriptor&0xffffff)
    dest = len(output)
    while index>stop:
        index-=1; control=data[index]
        for _ in range(8):
            if index<=stop or dest<=0: break
            if control&128:
                index-=2
                segment=struct.unpack_from('<H',data,index)[0]
                count=(segment>>12)+3; offset=(segment&4095)+2
                for _ in range(count):
                    if dest+offset>=len(output) or dest<=0: raise ValueError('BLZ bounds')
                    value=output[dest+offset];dest-=1;output[dest]=value
            else:
                index-=1;dest-=1;output[dest]=data[index]
            control=(control<<1)&255
    return bytes(output)

def main():
    p=argparse.ArgumentParser();p.add_argument('cci',type=pathlib.Path);p.add_argument('code',type=pathlib.Path);p.add_argument('report',type=pathlib.Path);p.add_argument('--romfs',type=pathlib.Path);a=p.parse_args()
    with a.cci.open('rb') as f:
        header=f.read(512)
        if header[256:260]!=b'NCSD': raise ValueError('NCSD missing')
        base=struct.unpack_from('<I',header,288)[0]*512
        f.seek(base);ncch=f.read(512)
        if ncch[256:260]!=b'NCCH':raise ValueError('NCCH missing')
        exefs=base+struct.unpack_from('<I',ncch,416)[0]*512
        f.seek(exefs);files=f.read(512)
        found=False
        for n in range(10):
            name,offset,size=struct.unpack_from('<8sII',files,n*16)
            if name.rstrip(b'\0')==b'.code':
                f.seek(exefs+512+offset);packed=f.read(size);found=True;break
        if not found:raise ValueError('code entry missing')
        f.seek(base+512);exheader=f.read(1024)
        code=decompress(packed) if exheader[13]&1 else packed
        expected=a.code.read_bytes()
        if code!=expected:raise ValueError('CCI code does not match external ExeFS')
        romfs=base+struct.unpack_from('<I',ncch,432)[0]*512
        f.seek(romfs);magic=f.read(4)
        if magic!=b'IVFC':raise ValueError('Readable RomFS IVFC missing')
        matched=compare_romfs(f,romfs+4096,a.romfs) if a.romfs else None
    report={'cci':a.cci.name,'partition_offset':hex(base),'title_id':f'{struct.unpack_from("<Q",ncch,280)[0]:016X}','code_bytes':len(code),'code_sha256':hashlib.sha256(code).hexdigest(),'external_code_match':True,'romfs_readable_ivfc':True,'romfs_full_file_comparison':'NOT_RUN'}
    if matched is not None:report.update(romfs_full_file_comparison='PASS',romfs_matched_files=matched)
    a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
