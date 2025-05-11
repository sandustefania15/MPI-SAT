
import time

def resolve(ci, cj):
    """Perform resolution between two clauses ci and cj."""
    resolvents = set()
    for literal in ci:
        if -literal in cj:
            resolvent = (ci - {literal}) | (cj - {-literal})
            resolvents.add(frozenset(resolvent))
    return resolvents


def parse_dimacs_cnf(file_path):
    """Parse a DIMACS .cnf file and return a list of clauses as sets."""
    clauses = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '' or line.startswith('c') or line.startswith('p'):
                continue
            literals = [int(x) for x in line.split() if x != '0']
            if literals:
                clauses.append(set(literals))
    return clauses


def resolution_algorithm(clauses):
    """Check satisfiability using resolution, avoiding redundant pairs."""
    clauses = set(frozenset(clause) for clause in clauses)
    new = set()
    processed_pairs = set()
    

    while True:
        for ci in clauses:
            for cj in clauses:
                if ci == cj:
                    continue
                pair = tuple(sorted([ci, cj], key=id))
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)

                 
                if len(processed_pairs) % 100 == 0:
                    with open("res_log.txt", "a") as log_file:
                        log_file.write(f"Checked {len(processed_pairs)} clause pairs so far...\n")

                resolvents = resolve(ci, cj)
                if frozenset() in resolvents:
                    return False
                new |= resolvents

        if new.issubset(clauses):
            return True  

        clauses |= new 


if __name__ == "__main__":
    file_path = "input.cnf"
    output_file = "outputR.txt" 

    clauses = parse_dimacs_cnf(file_path)

    start_time = time.time()
    result = resolution_algorithm(clauses)
    end_time = time.time()

    with open(output_file, "w") as f:
        f.write(f"Satisfiable? {result}\n")
        f.write(f"Time taken: {end_time - start_time:.4f} seconds\n")
