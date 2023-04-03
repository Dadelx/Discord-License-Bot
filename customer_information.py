import json

class check:
  def __init__(self, customer_id):
    self.customer_id = customer_id

  def id(self, customer_id):
    with open('customers.json') as customer_file:
      custo = json.load(customer_file)
    customers = custo["customers"]
    if customer_id in customers[0]:
      return True
