    import random
    import math
    from faker import Faker


    def generatePeople(count, lowestFloor, highestFloor, maxTimeSpan, outfileName):
      fake = Faker()
      people = []

      groupSpan = int(math.ceil(maxTimeSpan / 12))
      zeroCount = int(math.ceil(count / 25))

      # Generate unique names
      names = set()
      while len(names) < count:
        names.add(fake.unique.first_name())
      names = list(names)

      # Time clusters creation
      clusterSize = maxTimeSpan / 4
      timeClusters = [
          random.uniform(i * clusterSize, (i + 1) * clusterSize) for i in range(4)
      ]

      for i in range(count):
        selectionGroup = random.choices([1, 2, 3], weights=[0.45, 0.40, 0.15],
                                        k=1)[0]
        if selectionGroup == 1:
          startFloor = lowestFloor
          endFloor = random.randint(lowestFloor + 1, highestFloor)
        elif selectionGroup == 2:
          startFloor = random.randint(lowestFloor + 1, highestFloor)
          endFloor = lowestFloor
        else:
          startFloor = random.randint(lowestFloor, highestFloor)
          endFloor = random.choice(
              [x for x in range(lowestFloor, highestFloor + 1) if x != startFloor])

        time = int(random.choice(timeClusters)) + random.randint(-groupSpan, groupSpan)

        if time < 0:
          time = 0
        elif zeroCount > 0:
          time = 0
          zeroCount -= 1

        people.append((names[i], startFloor, endFloor, int(time)))

      # Output the people's data
      sortedPeople = sorted(people, key=lambda x: x[3])
      with open(outfileName, 'w') as f:
        for name, start, end, time in sortedPeople:
          #print(f"{name}\t{start}\t{end}\t{time}")
          f.write(f"{name}\t{start}\t{end}\t{time}\n")


#generatePeople(10, 1, 8, 60, "hotel_slow.ppl")
#generatePeople(50, 1, 8, 2 * 60, "hotel_busy.ppl")
#generatePeople(100, 1, 44, 2 * 60, "highrise_slow.ppl")
#generatePeople(300, 1, 44, 5 * 60, "highrise_busy.ppl")