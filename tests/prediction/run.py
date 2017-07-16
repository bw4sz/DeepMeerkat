import logging
from modules import predict

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  predict.run()
