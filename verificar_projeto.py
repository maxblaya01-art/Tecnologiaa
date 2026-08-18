from pathlib import Path

required = [
    Path("main.py"),
    Path("buildozer.spec"),
    Path(".github/workflows/build-apk.yml"),
]

missing = [str(p) for p in required if not p.exists()]
if missing:
    print("FALTANDO:")
    for p in missing:
        print(" -", p)
    raise SystemExit(1)

print("OK - projeto pronto para GitHub Actions.")
