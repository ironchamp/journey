ids = []
# Take any a list of numbers and identify if any gaps
# Assumes numbers expected to start at 1 - so, negatives or zeros ignored
expect = 1
ids = [3, 2, 0, -1, 5, 2, 6, 8, 2, 10, 11, 13, -3]
ids.sort()
print(ids)
previous = -100  # effectively undefined
for id in ids:
    if id == previous:
        print("WARNING: Duplicate unexpected number is", id)
        # expected remains unchanged
    else:
        while id > expect:
            # until expected catches up with the actual list
            print("ERROR: Missing expected number is", expect)
            expect += 1
        if id == expect:
            # print("INFO: Expected number", expect, "matches", id)
            expect += 1
    previous = id
