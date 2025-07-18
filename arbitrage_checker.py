import requests

USDC = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
WETH = "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"

uniswap_api = "https://api.thegraph.com/subgraphs/name/ianlapham/arbitrum-dev"
sushiswap_api = "https://api.thegraph.com/subgraphs/name/sushiswap/arbitrum-exchange"

def get_price(pool_api, tokenA, tokenB):
    query = """
    {
      pairs(where: {token0: "%s", token1: "%s"}) {
        token0Price
        token1Price
      }
    }
    """ % (tokenA.lower(), tokenB.lower())
    resp = requests.post(pool_api, json={'query': query})
    data = resp.json()
    pairs = data['data']['pairs']
    if not pairs:
        return None, None
    return float(pairs[0]['token0Price']), float(pairs[0]['token1Price'])

def check_arbitrage():
    try:
        uni0, uni1 = get_price(uniswap_api, USDC, WETH)
        sushi0, sushi1 = get_price(sushiswap_api, USDC, WETH)
        if None in [uni0, uni1, sushi0, sushi1]:
            return "❌ Pool non trouvé ou données indisponibles."
        msg = (
            f"Uniswap USDC/ETH: {uni0:.6f}\n"
            f"SushiSwap USDC/ETH: {sushi0:.6f}\n"
        )
        if uni0 > sushi0 * 1.002:
            msg += "🚨 ARBITRAGE: Vendre sur Uniswap, Acheter sur SushiSwap !"
        elif sushi0 > uni0 * 1.002:
            msg += "🚨 ARBITRAGE: Vendre sur SushiSwap, Acheter sur Uniswap !"
        else:
            msg += "Aucune opportunité d'arbitrage."
        return msg
    except Exception as e:
        return f"Erreur: {e}"
