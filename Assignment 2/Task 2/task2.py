# Task 2 - Gold vs Total Medals: Winter Olympics Ranking Analysis
# Jython UDF (Jython 2.7) registered by task2.pig as task2_udf.
#
# task2.pig groups the medal rows by Olympic year and passes the top three
# candidates of each ranking as a bag of (country_code, country_name, medals)
# tuples. This UDF assigns the rank numbers and builds the pretty-printed
# report block for one Winter Olympic Games:
#
#   2026 Milan-Cortina
#   By Gold Medals:
#   1. Norway (18) | 2. United States (12) | 3. Italy (10)
#   By Total Medals:
#   1. Norway (41) | 2. United States (33) | 3. Italy (30)

TOP_N = 3  # number of leading countries reported for each ranking


def _ranked_line(entries):
    """Rank (country_code, country_name, medals) tuples and format one line.

    Ranking rule: more medals ranks higher; ties are broken by country_code
    in ascending order. Example: in 2018 Germany and Norway both won 14 gold
    medals, so GER ranks ahead of NOR (yay, Germany #1 :D).
    Pig bags are unordered, so the tuples are sorted here even though
    task2.pig already selected them with the same rule.
    """
    ranked = sorted(entries, key=lambda entry: (-entry[2], entry[0]))[:TOP_N]
    return ' | '.join('%d. %s (%d)' % (rank, name, medals)
                      for rank, (code, name, medals) in enumerate(ranked, 1))


@outputSchema('report:chararray')
def format_games_report(year, host_city, top_gold, top_total):
    """Return the report block for one Games.

    The block ends with a newline; together with the record separator that
    PigStorage writes, this leaves one blank line between consecutive Games.
    """
    lines = ['%d %s' % (year, host_city),
             'By Gold Medals:',
             _ranked_line(top_gold),
             'By Total Medals:',
             _ranked_line(top_total)]
    return '\n'.join(lines) + '\n'
