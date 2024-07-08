import os
import time
import zipfile
import networkx as nx

from GraphletCompression import GraphletCompression


def measuring_file(file, edges):
    file_stats = os.stat(file)
    bpe = round(file_stats.st_size * 8 / edges, 4)
    # print(f"File ratio for file {file}: {bpe} bpe")
    return bpe


def measuring_files(files, edges):
    size = 0

    for file in files:
        file_stats = os.stat(file)
        size += file_stats.st_size

    bpe = round(size * 8 / edges, 4)
    print(f"File ratio for files: {bpe} bpe")
    return bpe


def create_zip_file(path_to_file, file, edges):
    archive_file = f"Output/{file}.zip"

    with zipfile.ZipFile(archive_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(path_to_file)

    file_stats = os.stat(archive_file)
    bpe = round(file_stats.st_size * 8 / edges, 4)
    print(f"Compression ratio for {file}: {round(file_stats.st_size * 8 / edges, 4)} bpe")
    return bpe


def create_zip_files(name, edges, files):
    archive_file = f"Output/{name}.zip"

    with zipfile.ZipFile(archive_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            zipf.write(file)

    file_stats = os.stat(archive_file)
    bpe = round(file_stats.st_size * 8 / edges, 4)
    print(f"Compression ratio {bpe} bpe")

    return bpe


def compress_and_zip(command, edges, path):
    res = os.system(command)

    if res != 0:
        print(f"Error {command} failed.")
        exit(0)

    os.system(f"mv {path} Output/")

    compressed_file = f"Output/{path.split('/')[1]}"

    bpe_original = measuring_file(compressed_file, edges)
    bpe_zip = create_zip_file(compressed_file, f"{path.split('/')[1]}", edges)

    return bpe_original, bpe_zip



def graphlet(G, name):
    gc = GraphletCompression("graphlets.txt")
    gc.compress(G, name)

    os.system(f"mv {name}_compressed.graph Output/")

    return create_zip_file(f"Output/{name}_compressed.graph", f"{name}_compressed.graph", len(G.edges()))


def read_graph(file):
    G = nx.DiGraph()

    with open(file, "r") as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue
            line = line.strip().split(" ")
            G.add_edge(int(line[0]), int(line[1]))

    return G



def main():
    G = read_graph("KnowledgeBase.edges")

    graphlet(G, "KnowledgeBase")


if __name__ == '__main__':
    st = time.time()

    main()

    et = time.time()
    elapsed_time = et - st

    print(f"Time: {elapsed_time / 60} minutes")
