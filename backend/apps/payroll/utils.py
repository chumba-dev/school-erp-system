from decimal import Decimal

def calculate_paye(gross, paye_brackets, personal_relief=2400):
    """
    Calculate PAYE based on monthly tax brackets.
    paye_brackets: list of dicts [{"up_to": amount, "rate": percentage}, ...]
    """
    if gross <= 0:
        return Decimal('0.00')
    tax = Decimal('0.00')
    remaining = gross
    lower_bound = 0
    for bracket in paye_brackets:
        upper = Decimal(str(bracket['up_to']))
        rate = Decimal(str(bracket['rate'])) / 100
        if remaining <= 0:
            break
        taxable = min(remaining, upper - lower_bound)
        tax += taxable * rate
        remaining -= taxable
        lower_bound = upper
    # Apply personal relief
    tax = max(tax - Decimal(str(personal_relief)), Decimal('0.00'))
    return tax.quantize(Decimal('0.01'))

def calculate_nhif(gross, schedule):
    """
    NHIF deduction based on income bands.
    schedule: list of dicts [{"min":0, "max":5999, "deduction":150}, ...]
    """
    for band in schedule:
        if gross >= Decimal(str(band['min'])) and gross <= Decimal(str(band['max'])):
            return Decimal(str(band['deduction']))
    # If above highest band, use highest deduction
    return Decimal(str(schedule[-1]['deduction']))

def calculate_nssf(gross, tier1_limit, tier1_rate, tier2_limit, tier2_rate):
    """
    NSSF Tier I and Tier II (employee contribution).
    """
    tier1_limit = Decimal(str(tier1_limit))
    tier1_rate = Decimal(str(tier1_rate)) / 100
    tier2_limit = Decimal(str(tier2_limit))
    tier2_rate = Decimal(str(tier2_rate)) / 100

    pensionable = min(gross, tier2_limit)
    tier1 = min(pensionable, tier1_limit) * tier1_rate
    tier2 = max(Decimal('0.00'), pensionable - tier1_limit) * tier2_rate
    return (tier1 + tier2).quantize(Decimal('0.01'))

def calculate_shif(gross, rate):
    """Social Health Insurance Fund (formerly SHA) – % of gross"""
    rate = Decimal(str(rate)) / 100
    return (gross * rate).quantize(Decimal('0.01'))

def calculate_housing_levy(gross, rate):
    """Housing Levy – % of gross"""
    rate = Decimal(str(rate)) / 100
    return (gross * rate).quantize(Decimal('0.01'))