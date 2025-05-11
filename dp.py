import time

def pure_literals(clauses):
    counter = {}
    for clause in clauses:
        for literal in clause:
            counter[literal] = counter.get(literal, 0) + 1
    return {lit for lit in counter if -lit not in counter}

def unit_propagate(clauses):
    unit_clauses = {next(iter(c)) for c in clauses if len(c) == 1}
    while unit_clauses:
        literal = unit_clauses.pop()
        new_clauses = set()
        for clause in clauses:
            if literal in clause:
                continue
            if -literal in clause:
                new_clause = set(clause)
                new_clause.remove(-literal)
                if not new_clause:
                    return None
                new_clauses.add(frozenset(new_clause))
            else:
                new_clauses.add(clause)
        clauses = new_clauses
        unit_clauses |= {next(iter(c)) for c in clauses if len(c) == 1}
    return clauses

def eliminate_pure_literals(clauses):
    pure = pure_literals(clauses)
    new_clauses = {clause for clause in clauses if not any(lit in pure for lit in clause)}
    return new_clauses

def resolve(ci, cj, literal):
    resolvent = (ci - {literal}) | (cj - {-literal})
    if any(lit in resolvent and -lit in resolvent for lit in resolvent):
        return None
    return frozenset(resolvent)

def dp_algorithm(clauses):
    clauses = set(frozenset(c) for c in clauses)
    resolved_pairs = set()
    log_counter = 0

    while True:
        clauses = unit_propagate(clauses)
        if clauses is None:
            with open("dp_log.txt", "a") as log:
                log.write("Conflict during unit propagation. UNSAT.\n")
            return False
        if not clauses:
            with open("dp_log.txt", "a") as log:
                log.write("All clauses satisfied during unit propagation. SAT.\n")
            return True

        clauses = eliminate_pure_literals(clauses)
        if not clauses:
            with open("dp_log.txt", "a") as log:
                log.write("All clauses satisfied after eliminating pure literals. SAT.\n")
            return True

        some_clause = min(clauses, key=len)
        literal = next(iter(some_clause))

        pos_clauses = {c for c in clauses if literal in c}
        neg_clauses = {c for c in clauses if -literal in c}
        others = {c for c in clauses if literal not in c and -literal not in c}

        resolvents = set()
        for ci in pos_clauses:
            for cj in neg_clauses:
                pair_id = tuple(sorted([id(ci), id(cj)]))
                if pair_id in resolved_pairs:
                    continue
                resolved_pairs.add(pair_id)
                log_counter += 1

                if log_counter % 100 == 0:
                    with open("dp_log.txt", "a") as log:
                        log.write(f"Resolved {log_counter} clause pairs so far...\n")

                resolvent = resolve(ci, cj, literal)
                if resolvent is None:
                    continue
                if not resolvent:
                    with open("dp_log.txt", "a") as log:
                        log.write("Derived empty clause. UNSAT.\n")
                    return False
                resolvents.add(resolvent)

        if not resolvents:
            with open("dp_log.txt", "a") as log:
                log.write("No resolvents generated. SAT.\n")
            return True

        clauses = others.union(resolvents)


def parse_dimacs_cnf(file_path):
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

if __name__ == "__main__":
    file_path = "input.cnf"
    output_file = "outputDP.txt"

    clauses = parse_dimacs_cnf(file_path)

    start_time = time.time()
    result = dp_algorithm(clauses)
    end_time = time.time()

    with open(output_file, "w") as f:
        f.write(f"Satisfiable? {result}\n")
        f.write(f"Time taken: {end_time - start_time:.4f} seconds\n")


