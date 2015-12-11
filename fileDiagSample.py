import time
def squares():
  for i in range(10):
    yield i * i # send data

for j in squares():
  print(j)
  time.sleep(1)