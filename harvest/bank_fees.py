from enum import Enum
import unittest
import pandas as pd
import json
import re

INSTITUTIONS_VERSION = 1

def get_institutions_file_path(version=INSTITUTIONS_VERSION):
    return "data/institutions_v{}.json".format(version)

def institutionsNameMap():
    institutions = loadInstitutions()
    map = {}
    for institution in institutions:
        map[institution['institution_id']] = institution['name']
    return map

def loadInstitutions(path=get_institutions_file_path()):
    with open(path ,'r') as file:
        institutions = json.load(file)
    return institutions

class BANK_FEES(Enum):
    OVERDRAFT = "Overdraft Fee"
    FOREIGN_TRANSACTION = "Foreign Transaction Fee"
    LATE = "Late Fee"
    WIRE = "Wire Transfer Fee"
    ACCOUNT_MAINTENANCE = "Account Maintenance Fee"
    MONTHLY_SERVICE = "Monthly Service Fee"
    MINIMUM_BALANCE = "Minimum Balance Fee"
    ATM = "ATM Fee"
    INTEREST = "Credit Card Interest Charges"
    NSF = "NSF Fees"
    CASH_ADVANCE = "Cash Advance"
    BALANCE_INQUIRY_FEE = "Balance Inquiry Fee"
    TRANSACTION_FEE = "Transaction Fee"
    EXCESS = "Excess Fee"
    CHECK_FEE = "Check Fee"
    STOP_PAYMENT_FEE = "Stop Payment Fee"
    EARLY_CLOSURE_FEE = "Early Closure Fee"
    DORMANT_FEE = "Dormant Fee"
    PAPER_STATEMENT = "Paper Statement Fee"
    CLOSED_ACCOUNT_PROCESING = "Closed Account Processing Fee"
    EXTERNAL_TRANSFER = "External Transfer Fee"
    CARD_SETUP = "Card setup fee"
    MEMBER = "Membership Fee"

class FEE_REFUNDS(Enum):
    OVERDRAFT = "Overdraft Refund"

REFUND_PROBABILITIES = {
    BANK_FEES.OVERDRAFT : "High",
    BANK_FEES.FOREIGN_TRANSACTION : "Low",
    BANK_FEES.LATE : "High",
    BANK_FEES.WIRE : "Low",
    BANK_FEES.ACCOUNT_MAINTENANCE : "Medium",
    BANK_FEES.MONTHLY_SERVICE : "High",
    BANK_FEES.MINIMUM_BALANCE : "High",
    BANK_FEES.ATM : "Low",
    BANK_FEES.INTEREST : "Low",
    BANK_FEES.NSF : "High",
    BANK_FEES.CASH_ADVANCE : "Medium",
    BANK_FEES.BALANCE_INQUIRY_FEE : "Low",
    BANK_FEES.TRANSACTION_FEE : "High",
    BANK_FEES.EXCESS : "High",
    BANK_FEES.STOP_PAYMENT_FEE : "Low",
    BANK_FEES.EARLY_CLOSURE_FEE : "Medium",
    BANK_FEES.DORMANT_FEE : "High",
    BANK_FEES.CLOSED_ACCOUNT_PROCESING : "Low",
    BANK_FEES.PAPER_STATEMENT : "Medium",
    BANK_FEES.CHECK_FEE : "Low",
    BANK_FEES.EXTERNAL_TRANSFER : "",
    BANK_FEES.CARD_SETUP : "",
    BANK_FEES.MEMBER: "Low"
}

REFUND_PROBABILITY_NORMALIZED = {
    "High": 1,
    "Medium": 0.3,
    "Low": 0.1
}

REFUND_MATCH_RULES = [
    (r"od.*fee.*refund", FEE_REFUNDS.OVERDRAFT),
    (r"od.*fee.*eraser", FEE_REFUNDS.OVERDRAFT),
    (r"od.*threshold.*refund", FEE_REFUNDS.OVERDRAFT),
    (r"od.*fee.*reversal", FEE_REFUNDS.OVERDRAFT),
    (r"overdraft.*fee.*refund", FEE_REFUNDS.OVERDRAFT),
    (r"overdraft.*fee.*eraser", FEE_REFUNDS.OVERDRAFT),
    (r"overdraft.*threshold.*refund", FEE_REFUNDS.OVERDRAFT),
    (r"overdraft.*fee.*reversal", FEE_REFUNDS.OVERDRAFT),
    (r"insufficient.*fee.*refund", FEE_REFUNDS.OVERDRAFT)
]

FEE_MATCH_RULES = [
    (r"tier.*overdraft.*item.*charge", BANK_FEES.OVERDRAFT),
    (r".*overdraft.*pos.*", BANK_FEES.OVERDRAFT),
    (r".*overdraft.*charge.*", BANK_FEES.OVERDRAFT),
    (r"consecutive.*od.*fee", BANK_FEES.OVERDRAFT),
    (r"miscellaneous.*service.*rpc", BANK_FEES.OVERDRAFT),
    (r"overdraft.*dr.*amt", BANK_FEES.OVERDRAFT),
    (r"Overdraft.*RPC", BANK_FEES.OVERDRAFT),
    (r"CONTINUOUS.*CHARGE.*DAY.*", BANK_FEES.OVERDRAFT),
    (r"od.*Tran.*Fee", BANK_FEES.OVERDRAFT),
    (r".*overdraft.*fee", BANK_FEES.OVERDRAFT),
    (r".*fee.*overdraft", BANK_FEES.OVERDRAFT),
    (r".*od.*fee", BANK_FEES.OVERDRAFT),
    (r".*overdraft.*ret", BANK_FEES.OVERDRAFT),
    (r".*sustained.*od", BANK_FEES.OVERDRAFT),
    (r".*negative.*account.*balance.*fee", BANK_FEES.OVERDRAFT),
    (r".*overdraft.*pd", BANK_FEES.OVERDRAFT),
    (r"courtesy.*pay.*fee", BANK_FEES.OVERDRAFT),
    (r"privilege.*pay", BANK_FEES.OVERDRAFT),
    (r"paid.*item.*fee", BANK_FEES.OVERDRAFT),
    (r"extended.*overdraft", BANK_FEES.OVERDRAFT),
    (r".*check fee", BANK_FEES.CHECK_FEE),
    (r".*international.*transaction.*fee", BANK_FEES.FOREIGN_TRANSACTION),
    (r".*foreign.*transaction.*fee", BANK_FEES.FOREIGN_TRANSACTION),
    (r".*foreign exchange rate adjustment fee", BANK_FEES.FOREIGN_TRANSACTION),
    (r".*transaction.*fee", BANK_FEES.TRANSACTION_FEE),
    (r"wire.*trans.*svc.*", BANK_FEES.WIRE),
    (r"wire.*trans.*fee", BANK_FEES.WIRE),
    (r"dormant.*fee", BANK_FEES.DORMANT_FEE),
    (r".*excess.*fee", BANK_FEES.EXCESS),
    (r".*excess.*withdrawl.*fee", BANK_FEES.EXCESS),
    (r".*atm fee-with", BANK_FEES.ATM),
    (r".*usage.*ATM", BANK_FEES.ATM),
    (r".*SURCHARGE.*FEE", BANK_FEES.ATM),
    (r".*withdraw.*fee", BANK_FEES.ATM),
    (r".*withdrwl.*fee", BANK_FEES.ATM),
    (r".*atm.*fee", BANK_FEES.ATM),
    (r"interest charge.*purchase", BANK_FEES.INTEREST),
    (r"interest charge.*standard", BANK_FEES.INTEREST),
    (r"purchase interest charge", BANK_FEES.INTEREST),
    (r"balance transfer interest", BANK_FEES.INTEREST),
    (r"interest charged to .*", BANK_FEES.INTEREST),
    (r"nsf return item fee for a transaction", BANK_FEES.NSF),
    (r"returned.*statement.*fee", BANK_FEES.PAPER_STATEMENT),
    (r"return.*item.*fee", BANK_FEES.NSF),
    (r"insufficient.*funds", BANK_FEES.NSF),
    (r"nsf.*returned.*item", BANK_FEES.NSF),
    (r".*return.*fee", BANK_FEES.NSF),
    (r".*nsf.*charge", BANK_FEES.NSF),
    (r"paid.*nsf", BANK_FEES.NSF),
    (r"nsf.*paid", BANK_FEES.NSF),
    (r"deposit.*returned", BANK_FEES.NSF),
    (r"cashed.*check.*returned", BANK_FEES.NSF),
    (r"nsf.*item.*returned", BANK_FEES.NSF),
    (r"return.*deposit.*item", BANK_FEES.NSF),
    (r".*item.*ret.*unpaid.*fee", BANK_FEES.NSF),
    (r"uncollected.*funds", BANK_FEES.NSF),
    (r"monthly.*service.*fee", BANK_FEES.MONTHLY_SERVICE),
    (r"monthly.*service.*charge", BANK_FEES.MONTHLY_SERVICE),
    (r"monthly.*srvc.*fee", BANK_FEES.MONTHLY_SERVICE),
    (r"monthly maintenance fee", BANK_FEES.ACCOUNT_MAINTENANCE),
    (r"account maintenance fee", BANK_FEES.ACCOUNT_MAINTENANCE),
    (r"account service charge", BANK_FEES.ACCOUNT_MAINTENANCE),
    (r"maintenance.*fee", BANK_FEES.ACCOUNT_MAINTENANCE),
    (r"late fee", BANK_FEES.LATE),
    (r"minimum balance fee", BANK_FEES.MINIMUM_BALANCE),
    (r"interest charge on promotional balances", BANK_FEES.INTEREST),
    (r".*bal.*inq.*fee", BANK_FEES.BALANCE_INQUIRY_FEE),
    (r".*stop.*payment.*fee", BANK_FEES.STOP_PAYMENT_FEE),
    (r".*early.*closure.*fee", BANK_FEES.EARLY_CLOSURE_FEE),
    (r"closed.*account.*processing.*fee", BANK_FEES.CLOSED_ACCOUNT_PROCESING),
    (r"paper.*statement.*fee", BANK_FEES.PAPER_STATEMENT),
    (r"undeliverable.*address.*fee", BANK_FEES.PAPER_STATEMENT),
    (r"undelivered.*address.*fee", BANK_FEES.PAPER_STATEMENT),
    (r"cash advance interest charge", BANK_FEES.CASH_ADVANCE),
    (r"ext.*trans.*fees", BANK_FEES.EXTERNAL_TRANSFER),
    (r"Debit.*setup.*fee", BANK_FEES.CARD_SETUP),
    (r".*membership.*fee", BANK_FEES.MEMBER)

]

def get_bank_fees(transaction):
    for regex, type in FEE_MATCH_RULES:
        if re.match(regex, transaction, flags=re.IGNORECASE):
            return type.value
    return False

def get_bank_fee_type(transaction):
    for regex, type in FEE_MATCH_RULES:
        if re.match(regex, transaction, flags=re.IGNORECASE):
            return type
    return False

def get_fee_refunds(transaction):
    for regex, type in REFUND_MATCH_RULES:
        if re.match(regex, transaction, flags=re.IGNORECASE):
            return type.value
    return False

class TestProcessor(unittest.TestCase):

    def setUp(self):
        pass

    def testInstitutions(self):
        iMap = institutionsNameMap()
        self.assertEqual(iMap['ins_25'], 'Ally Bank')

    def testFeeRefunds(self):
        data_tup = [
            ("OD Fee Itm 2175523030 Refund", FEE_REFUNDS.OVERDRAFT.value),
        ]
        for d in data_tup:
            print(d[0])
            self.assertEqual(get_fee_refunds(d[0]), d[1])

    def testBankFees(self):
        data = pd.Series.from_array([
            "Not a fee",
            "Overdraft Protection",
            "INTERNATIONAL TRANSACTION FEE",
            "Wire Transfer SVC",
            "Interest Charged on Purchases",
            "Purchase Interest Charge",
            "Balance Transfer Interest",
            "INTEREST CHARGED TO STANDARD",
            "Non-Chase ATM Withdraw Fee",
            "Non-Chase ATM FEE-WITH",
            "Interest Charge on Purchases",
            "NSF RETURN ITEM FEE FOR A TRANSACTION",
            "Cash Advance Interest Charge",
            "MONTHLY SERVICE FEE",
            "Interest Charge on Promotional Balances", "FOREIGN EXCHANGE RATE ADJUSTMENT FEE 03/03UBER 6PMY"
        ]).to_frame()
        classes = [
            False,
            False,
            BANK_FEES.FOREIGN_TRANSACTION.value,
            BANK_FEES.WIRE.value,
            BANK_FEES.INTEREST.value,
            BANK_FEES.INTEREST.value,
            BANK_FEES.INTEREST.value,
            BANK_FEES.INTEREST.value,
            BANK_FEES.ATM.value,
            BANK_FEES.ATM.value,
            BANK_FEES.INTEREST.value,
            BANK_FEES.NSF.value,
            BANK_FEES.CASH_ADVANCE.value,
            BANK_FEES.MONTHLY_SERVICE.value,
            BANK_FEES.INTEREST.value,
            BANK_FEES.FOREIGN_TRANSACTION.value,
        ]
        out = data[0].apply(get_bank_fees)
        self.assertEqual(out.tolist(), classes)
        data_tup = [
            ("MONTHLY Srvc Fee", BANK_FEES.MONTHLY_SERVICE.value),
            ("MONTHLY Service CHarge", BANK_FEES.MONTHLY_SERVICE.value),
            ("Non-usbank Atm Denied Fee", BANK_FEES.ATM.value),
            ("Atm Fee-bal Inq At Other Network", BANK_FEES.ATM.value),
            ("Atm Fee plusterm Laguna South Padre Txus", BANK_FEES.ATM.value),
            ("INTEREST CHARGED TO STANDARD", BANK_FEES.INTEREST.value),
            ("BAL INQ HUNTINGTON AV FEE", BANK_FEES.BALANCE_INQUIRY_FEE.value),
            ("Balance Inquiry Fee", BANK_FEES.BALANCE_INQUIRY_FEE.value),
            ("WITHDRWL HUNTINGTON AV BOSTON MA FEE", BANK_FEES.ATM.value),
            ("VARRIO / # WITHDRWL FIFTH AVENUE BROOKLYN NY FEE", BANK_FEES.ATM.value),
            ("foreign transaction fee", BANK_FEES.FOREIGN_TRANSACTION.value),
            ("official check fee", BANK_FEES.CHECK_FEE.value),
            ("FEE / CHECK# $ . RETURNED- NONSUFFICIENT FUNDS $.", BANK_FEES.NSF.value),
            ("NSF Fee With Image ACH Debit", BANK_FEES.NSF.value),
            ("NSF fee / In the amount $. CAPITAL ONE %% ACH ECC WEB", BANK_FEES.NSF.value),
            ("NSF fee / In the amount $. Acorns Investing %% ACH ECC WEB", BANK_FEES.NSF.value),
            ("NSF fee / In the amount $. EarninActivehour %% ACH ECC WEB", BANK_FEES.NSF.value),
            ("returned item fee", BANK_FEES.NSF.value),
            ("NSF: RETURNED ITEM FEE", BANK_FEES.NSF.value),
            ("NSF: CHARGE RETURNED ITEM", BANK_FEES.NSF.value),
            ("Returned Deposit Item Fee", BANK_FEES.NSF.value),
            ("NSF Fee - Item Returned", BANK_FEES.NSF.value),
            ("Cashed Check Returned", BANK_FEES.NSF.value),
            ("Deposited Check Returned", BANK_FEES.NSF.value),
            ("Deposited Item Returned", BANK_FEES.NSF.value),
            ("NSF CHARGE-RETURNED ITEM", BANK_FEES.NSF.value),
            ("CASHED/DEPOSITED ITEM RETN UNPAID FEE", BANK_FEES.NSF.value),
            ("Returned Deposited Item Fee", BANK_FEES.NSF.value),
            ("Returned Cashed Item Fee", BANK_FEES.NSF.value),
            ("Deposited Item Returned Penalty", BANK_FEES.NSF.value),
            ("Uncollected Funds item paid", BANK_FEES.NSF.value),
            ("Uncollected Funds item returned", BANK_FEES.NSF.value),
            ("UNITED SPRMRKTS DES:RETURN FEE ID: INDN:FILE X CO ID:-X PPD", BANK_FEES.NSF.value),
            ("NSF Charge", BANK_FEES.NSF.value),
            ("NSF CHARGE-PAID ITEM CHECK: $. CHECK CLEARED", BANK_FEES.NSF.value),
            ("NSF CHARGE-PAID ITEM $. DEBIT FOR CHECKCARD", BANK_FEES.NSF.value),
            ("NSF CHARGE-RETURNED ITEM", BANK_FEES.NSF.value),
            ("RECURRING OVERDRAFT SERVICE CHARGE", BANK_FEES.OVERDRAFT.values),
            ("OVERDRAFT ITEM CHARGE", BANK_FEES.OVERDRAFT.value),
            ("TIER OVERDRAFT ITEM CHARGE", BANK_FEES.OVERDRAFT.value),
            ("courtesy pay fee", BANK_FEES.OVERDRAFT.value),
            ("OVERDRAFT ITEM FEE FOR ACTIVITY OF - POSTING SEQ", BANK_FEES.OVERDRAFT.value),
            ("OVERDRAFT ITEM FEE FOR ACTIVITY OF - CHECK # POSTING DATE -- POSTING SEQ", BANK_FEES.OVERDRAFT.value),
            ("Continuous Overdraft Fee", BANK_FEES.OVERDRAFT.value),
            ("Overdraft protection transfer fee", BANK_FEES.OVERDRAFT.value),
            ("OD Fee- Item Paid", BANK_FEES.OVERDRAFT.value),
            ("Overdraft RET", BANK_FEES.OVERDRAFT.value),
            ("Overdraft Return Fee", BANK_FEES.OVERDRAFT.value),
            ("Overdraft Protection Transfer Fee", BANK_FEES.OVERDRAFT.value),
            ("Overdraft Transfer Fee", BANK_FEES.OVERDRAFT.value),
            ("Negative Account Balance Fee", BANK_FEES.OVERDRAFT.value),
            ("OD Item Fee", BANK_FEES.OVERDRAFT.value),
            ("Overdraft Assurance Line of Credit Product Fee", BANK_FEES.OVERDRAFT.value),
            ("Overdraft Sweep Fee", BANK_FEES.OVERDRAFT.value),
            ("Fee OVERDRAFT ( 1 AT $35 )", BANK_FEES.OVERDRAFT.value),
            ("Service Charge SUSTAINED OD", BANK_FEES.OVERDRAFT.value),
            ("Courtesy Pay Fee", BANK_FEES.OVERDRAFT.value),
            ("Savings Overdraft Protection Transfer Fee", BANK_FEES.OVERDRAFT.value),
            ("extended overdraft fee", BANK_FEES.OVERDRAFT.value),
            ("OVERDRAFT PD", BANK_FEES.OVERDRAFT.value),
            ("Privilege Pay Check Fee", BANK_FEES.OVERDRAFT.value),
            ("Privilege Pay Debit Fee",  BANK_FEES.OVERDRAFT.value),
            ("Privilege Pay Fee", BANK_FEES.OVERDRAFT.value),
            ("Privilege Pay ACH Fee", BANK_FEES.OVERDRAFT.value),
            ("Privilege Pay VCC Fee", BANK_FEES.OVERDRAFT.value),
            ("EXTENDED OVERDRAFT CHARGE", BANK_FEES.OVERDRAFT.value),
            ("Paid Item Fee", BANK_FEES.OVERDRAFT.value),
            ("Stop Payment Fee", BANK_FEES.STOP_PAYMENT_FEE.value),
            ("Early Closure Fee", BANK_FEES.EARLY_CLOSURE_FEE.value),
            ("Insufficient Funds Charge", BANK_FEES.NSF.value),
            ("Dormant Account Fee", BANK_FEES.DORMANT_FEE.value),
            ("Dormant Checking Fee", BANK_FEES.DORMANT_FEE.value),
            ("Dormant Savings Fee", BANK_FEES.DORMANT_FEE.value),
            ("Closed Account Processing Fee", BANK_FEES.CLOSED_ACCOUNT_PROCESING.value),
            ("Paper Statement Fee", BANK_FEES.PAPER_STATEMENT.value),
            ("UNDELIVERABLE STATEMENT FEE", BANK_FEES.PAPER_STATEMENT.value)
            ("Returned statement/Undeliverable address fee", BANK_FEES.PAPER_STATEMENT.value),
            ("Returned Statement Fee", BANK_FEES.PAPER_STATEMENT.value),
            ("Undelivered Address Fee", BANK_FEES.PAPER_STATEMENT.value),
            ("Excess fee", BANK_FEES.EXCESS.value),
            ("Excess Withdrawl fee", BANK_FEES.EXCESS.value),
            ("External Transfer Fee", BANK_FEES.EXTERNAL_TRANSFER.value),
            ("External Trans Fee", BANK_FEES.EXTERNAL_TRANSFER.value),
            ("Ext Trans Fee", BANK_FEES.EXTERNAL_TRANSFER.value),
            ("Debit Card setup fee", BANK_FEES.CARD_SETUP.value),
            ("Annual membership Fee", BANK_FEES.MEMBER.value),
            ("Membership Fee", BANK_FEES.MEMBER.value),
            ("USAGE FEE ATM", BANK_FEES.ATM.value),
            ("SURCHARGE FEE", BANK_FEES.ATM.value)


        ]
        for d in data_tup:
            print(d[0], d[1])
            self.assertEqual(get_bank_fees(d[0]), d[1])


if __name__ == "__main__":
    unittest.main()
