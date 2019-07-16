'''
resistorer/primitives test file
'''
import pytest

import resistorer.primitives as prims


@pytest.mark.xfail
@pytest.mark.parametrize('var', ['Q', 'F', 'A', 'X', 'Y'])
def test_get_unit_other_vars_returning_none(var):
    '''if unit is not in database, return None'''
    assert prims.get_unit(var) is None


@pytest.mark.xfail
@pytest.mark.parametrize('var,unit', list(prims.UNITS.items()))
def test_get_unit_lower_upper_case(var, unit):
    '''get_unit() should handle both upper and lower case arguments'''
    assert prims.get_unit(var.lower()) == unit
    assert prims.get_unit(var.upper()) == unit


@pytest.mark.parametrize('ph_r,ph_i,ph_u', [(1, 1, 1)])
def test_primitive_calculations_good(ph_r, ph_i, ph_u):
    '''Primitive should calculate proper values of voltage and current'''
    primitive = prims.Primitive(ph_r)
    primitive.ph_i = ph_i
    assert primitive.ph_u == ph_u
