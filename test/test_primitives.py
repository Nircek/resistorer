'''
resistorer/primitives test file
'''
from math import inf
import pytest

from str_holder import StrHolder

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
    assert prims.get_unit(var.upper()) == unit
    assert prims.get_unit(var.lower()) == unit


@pytest.mark.parametrize('ph_r,ph_i,ph_u', [(1, 1, 1), (75.5, 0.34, 25.67),
                                            (47e8, 1e-8, 47)])
def test_primitive_u_calculations_good(ph_r, ph_i, ph_u):
    '''Primitive should calculate proper values of voltage and current'''
    primitive = prims.Primitive(ph_r)
    primitive.ph_i = ph_i
    assert primitive.ph_u == ph_u


@pytest.mark.parametrize('ph_r,ph_i,ph_u', [(1, 1, 1), (75.5, 0.34, 25.67),
                                            (47e8, 1e-8, 47)])
def test_primitive_i_calculations_good(ph_r, ph_i, ph_u):
    '''Primitive should calculate proper values of voltage and current'''
    primitive = prims.Primitive(ph_r)
    primitive.ph_u = ph_u
    assert primitive.ph_i == ph_i


@pytest.mark.parametrize('ph_r,ph_i,ph_u', [(1, 0, 0), (1, inf, inf),
                                            (1, None, None)])
def test_primitive_u_abstract_calculations_good(ph_r, ph_i, ph_u):
    '''Primitive should calculate proper values of voltage and current'''
    primitive = prims.Primitive(ph_r)
    primitive.ph_i = ph_i
    assert primitive.ph_u == ph_u


@pytest.mark.xfail
@pytest.mark.parametrize('ph_r,ph_i', [(0, inf), (inf, 0)])
def test_primitive_u_too_abstract_calculations_good(ph_r, ph_i):
    '''Primitive should not calculate proper values of voltage and current if
    it's impossible and raise something.'''
    with pytest.raises(Exception):
        primitive = prims.Primitive(ph_r)
        primitive.ph_i = ph_i


@pytest.mark.xfail
@pytest.mark.parametrize('ph_r,ph_i,ph_u', [(0, inf, 1), (1, 0, 0),
                                            (1, inf, inf), (inf, 0, 1),
                                            (1, None, None)])
def test_primitive_i_abstract_calculations_good(ph_r, ph_i, ph_u):
    '''Primitive should calculate proper values of voltage and current'''
    primitive = prims.Primitive(ph_r)
    primitive.ph_u = ph_u
    assert primitive.ph_i == ph_i


TEST_ALL_DERIVERED_FROM_PRIMITIVE_HAS_OWN_STR_HOLDER = StrHolder()


@pytest.mark.parametrize('sub', prims.Primitive.__subclasses__() +
                         [prims.Primitive])
def test_all_derivered_from_primitive_has_own_str(sub):
    '''Every subclass of Primitive should has its own __str__ method result.'''
    if sub == prims.Delta:
        TEST_ALL_DERIVERED_FROM_PRIMITIVE_HAS_OWN_STR_HOLDER \
            .add(str(sub(*([None]*4))))
    else:
        TEST_ALL_DERIVERED_FROM_PRIMITIVE_HAS_OWN_STR_HOLDER.add(str(sub()))
