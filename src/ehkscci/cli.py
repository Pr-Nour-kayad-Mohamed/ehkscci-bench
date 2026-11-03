import argparse
from pathlib import Path
import json
from . import bench


def main():
    p=argparse.ArgumentParser(description="Exploratory EHK-SCCI benchmark")
    p.add_argument("command",choices=["demo","sweep","noise","cv"])
    p.add_argument("--n",type=int,default=16)
    p.add_argument("--repeats",type=int,default=12)
    p.add_argument("--windows",type=int,default=12)
    p.add_argument("--folds",type=int,default=3)
    p.add_argument("--seed",type=int,default=2026)
    p.add_argument("--out",default="results")
    args=p.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    jobs=("sweep","noise") if args.command=="demo" else (args.command,)
    for job in jobs:
        opts=dict(n=args.n,seed=args.seed)
        if job=="noise": opts["repeats"]=args.repeats
        if job=="cv": opts.update(windows=args.windows,folds=args.folds)
        df=getattr(bench,job)(**opts); df.to_csv(out/(job+".csv"),index=False)
        if job=="cv":
            means=df.groupby("tau_factor").auc.mean()
            selection=dict(tau_factor=float(means.idxmax()),validation_auc=float(means.max()),
                           warning="Selection score, not independent test performance")
            (out/"selection.json").write_text(json.dumps(selection,indent=2))
            print(json.dumps(selection,indent=2))
    (out/"parameters.json").write_text(json.dumps(vars(args),indent=2))

if __name__=="__main__": main()
