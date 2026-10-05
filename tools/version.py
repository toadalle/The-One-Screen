"""Increment exactly one independent version counter; never reset the others."""
import argparse,json,pathlib
def advance(version,counter):
    if counter not in ('major','milestone','iteration'):raise ValueError(counter)
    result=dict(version);result[counter]+=1;return result
def main():
    p=argparse.ArgumentParser();p.add_argument('counter',choices=['major','milestone','iteration']);args=p.parse_args()
    path=pathlib.Path(__file__).resolve().parents[1]/'VERSION.json'
    v=advance(json.loads(path.read_text()),args.counter);path.write_text(json.dumps(v,indent=2)+'\n');print('.'.join(str(v[k]) for k in ['major','milestone','iteration']))
if __name__=='__main__':main()
