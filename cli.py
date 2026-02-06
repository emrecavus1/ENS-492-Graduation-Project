import argparse
import json
from core.pipeline import run_pipeline


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sut", required=True, help="Path to sut.yaml")
    args = p.parse_args()

    output = run_pipeline(args.sut)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
