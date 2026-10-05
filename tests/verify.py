"""Host checks. These are not emulator or gameplay acceptance tests."""
import importlib.util,json,pathlib,struct,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build,version
class Contracts(unittest.TestCase):
    def test_independent_counters(self):
        self.assertEqual(version.advance({'major':1,'milestone':9,'iteration':99},'iteration'),{'major':1,'milestone':9,'iteration':100})
        self.assertEqual(version.advance({'major':1,'milestone':9,'iteration':100},'milestone'),{'major':1,'milestone':10,'iteration':100})
        self.assertEqual(version.advance({'major':1,'milestone':10,'iteration':100},'major'),{'major':2,'milestone':10,'iteration':100})
    def test_wrong_retail_rejected(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):build.validate_retail(b'wrong',[])
    def test_ips_roundtrip(self):
        sections=build.read_elf(ROOT/'.build/tos.elf')
        declarations=json.loads((ROOT/'config/patches.json').read_text())
        encoded,manifest=build.make_ips(sections,declarations)
        result=bytearray(0x600000);pos=5
        while encoded[pos:pos+3]!=b'EOF':
            offset=int.from_bytes(encoded[pos:pos+3],'big');size=int.from_bytes(encoded[pos+3:pos+5],'big');pos+=5
            self.assertGreater(size,0);result[offset:offset+size]=encoded[pos:pos+size];pos+=size
        self.assertEqual(pos+3,len(encoded))
        for name,address,data in sections:self.assertEqual(result[address-0x100000:address-0x100000+len(data)],data,name)
        header=(ROOT/'load/mods/0004000000033500/exheader.bin').read_bytes()
        addr,pages,_=struct.unpack_from('<III',header,0x30);bss=struct.unpack_from('<I',header,0x3c)[0]
        self.assertGreaterEqual(addr+pages*4096+((bss+4095)&~4095),max(a+len(b) for _,a,b in sections))
    def test_extent_rejected(self):
        with self.assertRaisesRegex(ValueError,'extent'):build.make_ips([('.patch_test',0x100000,b'123')],[{'name':'test','address':'0x100000','size':4}])
    def test_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError,'Overlapping'):build.make_ips([('.payload',0x610000,b'1234'),('.zero',0x610002,b'12')],[])
if __name__=='__main__':unittest.main(verbosity=2)
