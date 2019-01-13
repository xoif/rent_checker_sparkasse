import mt940
import pprint
import csv
import math

def parseTransactions():
    transaction_list = []
    mt940.tags.BalanceBase.scope = mt940.models.Transaction
    # The currency has to be set manually when setting the BalanceBase scope to Transaction.
    transactions = mt940.models.Transactions(processors=dict(
        pre_statement=[
            mt940.processors.add_currency_pre_processor('EUR'),
            mt940.processors.date_fixup_pre_processor,
        ],
    ))
    with open('./transactions.txt') as f:
        data = f.read()
    transactions.parse(data)
    for transaction in transactions:
        #add transaction sender, iban and amount if amount is positive
        amountString = str(transaction.data.get('amount'))[1:-4]
        amount = float(amountString)
        if amount > 0:
            transaction_list.append({"name": transaction.data.get("applicant_name"), "iban": transaction.data.get("applicant_iban"), "date": transaction.data.get("date"), "amount": amount})
    return transaction_list

def getTenantInfo():
    with open('./tenants.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        tenant_list = []
        for row in csv_reader:
            line = {"name": row.get("name"),"iban": row.get("iban"),"rent": float(row.get("rent"))}
            tenant_list.append(line)
            line_count += 1
        return tenant_list

transactions = parseTransactions()
tenant_info = getTenantInfo()

def checkRent(print_monthly):
    overall_payments = 0
    for tenant in tenant_info: 
        payments = 0
        for transaction in transactions:
            if tenant['iban'] in transaction.get('iban'):
                if math.isclose(tenant['rent'], transaction.get('amount'), rel_tol=1e-1):
                    payments += 1
                    if print_monthly: 
                       print(transaction.get('name'), "payed on", transaction.get('date'))
        print(tenant.get('name'), " payed ", payments, " times")
        if payments > 0:
            overall_payments += 1
    print(overall_payments, "of ", len(tenant_info), " payed")        

checkRent(False)        
