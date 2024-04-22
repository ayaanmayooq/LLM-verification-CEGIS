import matplotlib.pyplot as plt
import json
import scienceplots

plt.style.use('science')


if __name__ == "__main__":
    data = 'data/2024-04-22-09_30_57-NUM4.json'
    with open(data, "r") as f:
        data = json.load(f)
    stats = data["stats"]
    meta = data["meta"]
    print(stats, meta)
    title = f"Blocksworld {meta['num-blocks']} Number of Iterations per Setting"
    y=[stats["iters"]]
    x=[meta['model_type']]
    plt.bar([0,1], [y,6])
    plt.title(title)
    plt.xlabel("Setting")
    plt.ylabel("Number of Iterations")
    plt.show()