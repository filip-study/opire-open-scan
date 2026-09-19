# opire-open-scan

Pull [Opire](https://opire.dev) rewards and keep only **OPEN** GitHub issues that look claimable.

Boards love listing dollars on **closed**, **deleted**, or **farmed** issues. This CLI:

1. Fetches `https://api.opire.dev/rewards`
2. Verifies each linked GitHub issue is still `open` via `gh`
3. Drops farm repos / overcrowded claim queues
4. Prints a ranked table (low heat first)

Sibling of [bounty-freshness](https://github.com/filip-study/bounty-freshness) (paste-your-own-URLs). This one scans the Opire feed for you.

## Use

```bash
gh auth login   # once
python3 opire_open_scan.py
python3 opire_open_scan.py --max-heat 5 --min-usd 20
python3 opire_open_scan.py --json
```

Offline / CI:

```bash
curl -sS -A opire-open-scan https://api.opire.dev/rewards -o rewards.json
python3 opire_open_scan.py --opire-json rewards.json
```

## Smoke (this box)

```bash
python3 opire_open_scan.py --opire-json rewards.json --max-heat 40 --min-usd 5
```

## Tip jar (optional)

Base USDC tips keep the grind going:

- Tip: https://shieldz.cash/tip/tip-d2599a4d16a6f4b0
- Unlock pack: https://shieldz.cash/unlock/NDS0MgohhA3PmPaBvmD0
- Treasury: `0xbAd41cF0f0d5442f9A53630F8081BFd257DA019b`

## Related

- [bounty-freshness](https://github.com/filip-study/bounty-freshness) — check a URL list
- [base-usdc-tip-kit](https://github.com/filip-study/base-usdc-tip-kit) — tipcheck CLI
- [free-rpc-map](https://github.com/filip-study/free-rpc-map) — no-key Base/ETH RPCs

## License

MIT

## Buy today's USDC lanes snapshot ($3)

https://shieldz.cash/unlock/SUxX9gr_Yvxl8dQVbBQm

Tips: https://shieldz.cash/tip/tip-d2599a4d16a6f4b0

