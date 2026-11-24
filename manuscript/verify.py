import argparse
from fractions import Fraction
from hashlib import sha256
import json
from math import comb
from pathlib import Path


def add(left, right):
    length = max(len(left), len(right))
    return [(left[index] if index < len(left) else 0) +
            (right[index] if index < len(right) else 0) for index in range(length)]


def scale(polynomial, scalar):
    return [scalar * coefficient for coefficient in polynomial]


def multiply(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for left_degree, left_coefficient in enumerate(left):
        for right_degree, right_coefficient in enumerate(right):
            result[left_degree + right_degree] += left_coefficient * right_coefficient
    return result


def derivative(polynomial):
    return [degree * polynomial[degree] for degree in range(1, len(polynomial))]


def catalan_transform(limit):
    catalans = [comb(2 * index, index) // (index + 1) for index in range(limit + 1)]
    coefficients = [0] * (limit + 1)
    for catalan_index, catalan in enumerate(catalans):
        for choice in range(min(catalan_index, (limit - catalan_index) // 2) + 1):
            degree = catalan_index + 2 * choice
            contribution = (-1) ** choice * comb(catalan_index, choice) * catalan
            coefficients[degree] += contribution
            if degree < limit:
                coefficients[degree + 1] += contribution
    return coefficients, catalans


def convolution_partial_sums(limit):
    coefficients = [0] * (limit + 2)
    for index in range(1, limit + 2):
        coefficients[index] = int(index == 1) - int(index == 3) + sum(
            coefficients[split] * coefficients[index - split]
            for split in range(1, index))
    partial_sums = []
    running = 0
    for coefficient in coefficients[1:]:
        running += coefficient
        partial_sums.append(running)
    return partial_sums, coefficients


def recurrence_sequence(limit):
    coefficients = [1, 2, 3, 6]
    for index in range(4, limit + 1):
        numerator = -sum(factor * coefficients[index - lag] for lag, factor in [
            (1, -5 * index + 1), (2, 2 * (2 * index - 1)),
            (3, 2 * (2 * index - 7)), (4, 2 * (-2 * index + 7))])
        quotient, remainder = divmod(numerator, index + 1)
        assert remainder == 0, ('integrality', index)
        coefficients.append(quotient)
    return coefficients[:limit + 1]


def bilinear(values, index):
    first, second, third, fourth, fifth = values[index:index + 5]
    return (first * (16 * second - 64 * fourth + 22 * fifth) +
            second * (32 * third - 14 * fourth) +
            third * (16 * fourth - 10 * fifth) + fourth * (2 * fourth + fifth))


def linear_product(left, right):
    product = {}
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            key = tuple(sorted((left_index, right_index)))
            product[key] = product.get(key, 0) + left_value * right_value
    return product


def symbolic_elimination():
    first = linear_product([6, 0, 6, -3, 0], [0, 4, 0, -4, 1])
    second = linear_product([0, 2, 0, 10, -4], [4, 0, -4, 1, 0])
    difference = {key: first.get(key, 0) - second.get(key, 0)
                  for key in set(first) | set(second)}
    difference = {key: value for key, value in difference.items() if value}
    assert difference == {(0, 1): 16, (0, 3): -64, (0, 4): 22,
                          (1, 2): 32, (1, 3): -14, (2, 3): 16,
                          (2, 4): -10, (3, 3): 2, (3, 4): 1}
    short = [(1, 0), (-4, 6), (0, 0), (4, -18), (8, -48), (0, 0)]
    lagged = [(0, 0), (1, -1), (-4, 10), (0, 0), (4, -22), (8, -56)]
    combined = [(direct[0] + 5 * lag[0], direct[1] + 5 * lag[1])
                for direct, lag in zip(short, lagged)]
    assert combined == [(1, 0), (1, 1), (-20, 50), (4, -18),
                        (28, -158), (40, -280)]
    for degree, coefficient in enumerate([1, -4, 0, 4, 8]):
        derivative_contribution = -2 * degree * coefficient
        multiplier_contribution = -degree * coefficient
        assert derivative_contribution + multiplier_contribution == -3 * degree * coefficient
    assert [(-3 * degree * coefficient) for degree, coefficient in
            enumerate([1, -4, 0, 4, 8])] == [0, 12, 0, -36, -96]


def radical_family_checks():
    polynomials = [[1, -4, 0, 4], [1, -4, 0, 4, 8],
                   [1, 2, -3, 5, 0, 7], [1, 0, 0, -1]]
    for polynomial in polynomials:
        coefficients = [Fraction(0)]
        for index in range(1, 31):
            constant = -Fraction(polynomial[index], 4) if index < len(polynomial) else 0
            coefficients.append(constant + sum(
                coefficients[split] * coefficients[index - split]
                for split in range(1, index)))
        for index in range(1, 31):
            residual = sum(Fraction(value) * (index - Fraction(3 * degree, 2)) *
                           coefficients[index - degree]
                           for degree, value in enumerate(polynomial) if degree <= index)
            expected = -Fraction(index * polynomial[index], 4) if index < len(polynomial) else 0
            assert residual == expected, ('general radical', polynomial, index)
    return {'polynomials': polynomials, 'coefficient_range': [1, 30]}


def neighboring_sequence(limit):
    values = [0, 1, 1, 1, 1]
    for index in range(5, limit + 1):
        values.append(sum(values[split] * values[index - split]
                          for split in range(1, index)))
    return values


def short_neighbor(values, index):
    return (index * values[index] - (4 * index - 6) * values[index - 1] +
            (4 * index - 18) * values[index - 3] +
            8 * (index - 6) * values[index - 4])


def long_neighbor(values, index):
    return sum((slope * index + intercept) * values[index - lag]
               for lag, (slope, intercept) in enumerate([
                   (1, 0), (1, 1), (-20, 50), (4, -18),
                   (28, -158), (40, -280)]))


def table_comparison(values, table, start, end):
    if table is None:
        return None
    entries = {}
    for line in table.read_text().splitlines():
        body = line.split('#', 1)[0].strip()
        if body:
            index, value = map(int, body.split())
            assert index not in entries
            entries[index] = value
    assert all(index in entries for index in range(start, end + 1))
    assert all(values[index] == entries[index] for index in range(start, end + 1))
    return {'matched_terms': end - start + 1, 'range': [start, end],
            'source_sha256': sha256(table.read_bytes()).hexdigest()}


def run(limit, table, sibling_table, neighbor_table):
    discriminant = [1, -4, 0, 4]
    quadratic = [0, 1, -1]
    euler_polynomial = [1, -5, 4, 4, -4]
    multiplier = [1, -4, 6, -2, -2]
    assert multiply([1, -1], discriminant) == euler_polynomial
    assert add(scale(multiply(discriminant, derivative(quadratic)), 2),
               scale(multiply(derivative(discriminant), quadratic), -1)) == scale(multiplier, 2)
    assert scale(derivative(discriminant), -1) == [4, 0, -12]
    assert add(scale(multiply([0, 1], derivative(discriminant)), -1),
               [-3, 8]) == scale(discriminant, -3)
    assert add(multiply([0, 1], [4, 0, -4]), [-1]) == scale(discriminant, -1)
    symbolic_elimination()
    transformed, catalans = catalan_transform(limit)
    partial_sums, sibling = convolution_partial_sums(limit)
    recurrent = recurrence_sequence(limit)
    assert transformed == partial_sums == recurrent
    assert transformed[:8] == [1, 2, 3, 6, 14, 37, 105, 312][:min(limit + 1, 8)]
    for index in range(limit + 1):
        formula = sum((-1) ** ((index - rank) * (index - rank - 1) // 2) *
                      comb(rank, (index - rank) // 2) * catalans[rank]
                      for rank in range(index + 1) if (index - rank) // 2 <= rank)
        assert formula == transformed[index], ('binomial a', index)
        residual = sum((euler_polynomial[lag] * (index - lag) + multiplier[lag]) *
                       transformed[index - lag] for lag in range(min(index, 4) + 1))
        assert residual == int(index == 0) - 3 * int(index == 2), ('ODE', index)
    for index in range(1, limit + 2):
        formula = sum((-1) ** choice * comb(index - 2 * choice, choice) *
                      catalans[index - 2 * choice - 1]
                      for choice in range((index - 1) // 2 + 1)
                      if choice <= index - 2 * choice)
        assert formula == sibling[index], ('binomial b', index)
        assert sibling[index] > 0
        if index >= 4:
            assert index * sibling[index] == (2 * (2 * index - 3) * sibling[index - 1] -
                                             2 * (2 * index - 9) * sibling[index - 3])
    for index in range(1, limit - 2):
        assert bilinear(sibling, index) == 0, ('bilinear b', index)
    shifted = sibling[2:]
    shifted_formula_limit = min(limit - 1, 100)
    for index in range(shifted_formula_limit + 1):
        formula = sum(catalans[rank] * sum(
            (-1) ** choice * comb(rank + 1, choice) *
            comb(index - choice, index - 2 * rank - choice) *
            2 ** (index - 2 * rank - choice)
            for choice in range(min(rank + 1, index - 2 * rank) + 1))
                      for rank in range(index // 2 + 1))
        assert formula == shifted[index], ('shifted binomial', index)
        if index >= 2:
            assert shifted[index] == 2 * shifted[index - 1] + sum(
                shifted[split] * shifted[index - 2 - split]
                for split in range(index - 1))
    for index in range(max(0, limit - 4)):
        assert bilinear(shifted, index) == 0, ('shifted bilinear', index)
    for values in (sibling, neighboring_sequence(limit)):
        initial_length = 3 if values is sibling else 4
        adamson = values[1:]
        for index in range(initial_length, len(adamson)):
            assert adamson[index] == adamson[index - 1] + sum(
                adamson[split] * adamson[index - 1 - split]
                for split in range(index - 1)), ('Adamson construction', initial_length, index)
    row_limit = min(limit, 30)
    rows = [[1], [0, 1], [1]]
    for index in range(3, row_limit + 1):
        row = [0]
        for split in range(index):
            row = add(row, multiply(rows[split], rows[index - 1 - split]))
        rows.append(row)
    assert [sum(row) for row in rows] == sibling[1:row_limit + 2]
    neighbor = neighboring_sequence(limit)
    assert neighbor[1:9] == [1, 1, 1, 1, 4, 11, 32, 95][:limit]
    for index in range(5, limit + 1):
        assert short_neighbor(neighbor, index) == 0, ('short A025268', index)
    for index in range(6, limit + 1):
        assert long_neighbor(neighbor, index) == 0, ('six-term A025268', index)
    if limit >= 5:
        assert long_neighbor(neighbor, 5) == -40
    external = table_comparison(transformed, table, 0, limit)
    external_sibling = table_comparison(sibling, sibling_table, 1, limit + 1)
    external_neighbor = table_comparison(neighbor, neighbor_table, 1, limit)
    encoding = ''.join(f'{index} {value}\n' for index, value in enumerate(transformed)).encode()
    return {'arithmetic': 'unbounded integers', 'binomial_formulas': 'pass',
            'bilinear_a025262_range': [1, limit - 3],
            'bilinear_elimination_polynomial': 'pass',
            'general_radical_recurrence_coefficient': 'p_j*(n-3*j/2)',
            'general_radical_family': radical_family_checks(),
            'asymptotic_constant_polynomial_reductions': 'pass',
            'a056010_binomial_and_convolution_range': [0, shifted_formula_limit],
            'a056010_bilinear_range': [0, limit - 5] if limit >= 5 else None,
            'adamson_constructions': 'pass',
            'a025262_external_table': external_sibling,
            'a176703_polynomial_row_sum_range': [0, row_limit],
            'a025268_short_recurrence_range': [5, limit],
            'a025268_six_term_range': [6, limit],
            'a025268_zero_extended_n5': -40,
            'a025268_external_table': external_neighbor,
            'coefficient_ode': 'pass', 'constructions_compared': [
                'Catalan substitution', 'quadratic convolution and partial sums',
                'five-term recurrence'], 'external_oeis_table': external,
            'main_sequence_range': [0, limit], 'polynomial_identities': 'pass',
            'prefix': transformed[:8], 'sequence_encoding_sha256': sha256(encoding).hexdigest(),
            'sibling_range': [1, limit + 1], 'sibling_recurrence_and_positivity': 'pass'}


def main():
    parser = argparse.ArgumentParser(description='Exact coefficient checks for the Catalan transform.')
    parser.add_argument('--limit', type=int, default=1000)
    parser.add_argument('--oeis-table', type=Path)
    parser.add_argument('--sibling-table', type=Path)
    parser.add_argument('--neighbor-table', type=Path)
    arguments = parser.parse_args()
    if not 8 <= arguments.limit <= 2000:
        parser.error('--limit must lie between 8 and 2000')
    print(json.dumps(run(arguments.limit, arguments.oeis_table,
                         arguments.sibling_table, arguments.neighbor_table),
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
