#! /usr/bin/python
import random
from functools import wraps

from unittest import TestCase
from mock import Mock, patch
from nose.tools import raises

from drekdice.dice import Roll


def loaded_dice(result):
    """
    Patch random.randrange to provide an expected set of results.
    """

    def loaded(f):

        it = iter(result)
        @patch.object(random, "randrange", lambda x,y: it.next())
        @wraps(f)
        def wrapped(*args, **kwargs):
            f(*args, **kwargs)
        return wrapped

    return loaded


class RollTestCase(TestCase):

    @raises(ValueError)
    def test_dice_pool_negative_valueerror(self):
        """
        Test that passing a negative number of dice raises a ValueError.
        """

        dice = Roll(-1)

    @raises(ValueError)
    def test_dice_pool_zero_valueerror(self):
        """
        Test that passing 0 number of dice raises a ValueError.
        """

        dice = Roll(0)

    @raises(ValueError)
    def test_dice_pool_not_int_valueerror(self):
        """
        Test that passing a value that is not a number as number of dice
        raises a ValueError.
        """

        dice = Roll("foo")

    def test_dice_pool_no_edge(self):
        """
        Test that the correct number of dice is rolled when Edge is not used.
        """

        roll = Roll(3)
        self.assertEquals(roll.dice_pool, 3)
        roll = Roll(4)
        self.assertEquals(roll.dice_pool, 4)

    @loaded_dice([1, 2, 6, 6, 5, 2])
    def test_no_edge_six_not_explode(self):
        """
        Test that sixes do not explode when Edge is not used.
        """

        roll = Roll(3)
        self.assertEquals(roll.dice_pool, 3)
        self.assertEquals(roll.original_dice_pool, 3)
        self.assertEquals(roll.dice, [1, 2, 6])

    @loaded_dice([1, 6, 5, 2, 1])
    def test_edge_six_explode(self):
        """
        Test that sixes explode and generate more dice when using Edge.
        """

        roll = Roll(3, edge=True)
        self.assertEquals(roll.dice_pool, 4)
        self.assertEquals(roll.original_dice_pool, 3)
        self.assertEquals(roll.dice, [1, 6, 5, 2])

    @loaded_dice([1, 6, 6, 5, 2, 1])
    def test_edge_six_explode_sequence(self):
        """
        Test that a sequence of sixes keep exploding and generate more dice
        when Edge is used.
        """

        roll = Roll(3, edge=True)
        self.assertEquals(roll.dice_pool, 5)
        self.assertEquals(roll.original_dice_pool, 3)
        self.assertEquals(roll.dice, [1, 6, 6, 5, 2])

    @loaded_dice([1, 6, 5, 6, 1, 1])
    def test_edge_six_explode_multiple(self):
        """
        Test that multiple sixes all explode when Edge is used.
        """

        roll = Roll(3, edge=True)
        self.assertEquals(roll.dice_pool, 5)
        self.assertEquals(roll.original_dice_pool, 3)
        self.assertEquals(roll.dice, [1, 6, 5, 6, 1])

    @loaded_dice([1, 5, 5, 5, 2, 1])
    def test_edge_five_not_explode(self):
        """
        Test that fives, which are also hits, do not explode when Edge is used.
        """

        roll = Roll(3, edge=True)
        self.assertEquals(roll.dice_pool, 3)
        self.assertEquals(roll.original_dice_pool, 3)
        self.assertEquals(roll.dice, [1, 5, 5])

    @loaded_dice([5, 1, 2, 3])
    def test_hits_positive(self):
        """
        Test that a positive number of hits is correctly reported.
        """

        roll = Roll(4)
        self.assertEquals(roll.hits, 1)

    @loaded_dice([2, 1, 2, 3])
    def test_hits_none(self):
        """
        Test that no hits are correctly reported.
        """

        roll = Roll(4)
        self.assertEquals(roll.hits, 0)

    @loaded_dice([5, 6, 6, 5, 6])
    def test_hits_all(self):
        """
        Test that all hits of a roll are correctly reported.
        """

        roll = Roll(5)
        self.assertEquals(roll.hits, 5)

    @loaded_dice([2, 1, 2, 1])
    def test_glitches_positive(self):
        """
        Test that a postive number of glitches is correctly reported.
        """

        roll = Roll(4)
        self.assertEquals(roll.glitches, 2)

    @loaded_dice([2, 3, 2, 4])
    def test_glitches_none(self):
        """
        Test that no glitches are correctly reported.
        """

        roll = Roll(4)
        self.assertEquals(roll.glitches, 0)

    @loaded_dice([1, 1, 1, 1])
    def test_glitches_all(self):
        """
        Test that all glitches of a roll are correctly reported.
        """

        roll = Roll(4)
        self.assertEquals(roll.glitches, 4)

    @loaded_dice([1, 1, 5, 2])
    def test_glitch_equal_threshold_true(self):
        """
        Test that a glitch occurs when half the dice are glitches.
        """

        roll = Roll(4)
        self.assertTrue(roll.glitch)

    @loaded_dice([1, 2, 5])
    def test_glitch_under_threshold_false(self):
        """
        Test that a glitch does not occur when under half the dice are glitches.
        """

        roll = Roll(3)
        self.assertFalse(roll.glitch)

    @loaded_dice([1, 1, 4])
    def test_glitch_over_threshold_true(self):
        """
        Test that a glitch occurs when over half of the dice are glitches.
        """

        roll = Roll(3)
        self.assertTrue(roll.glitch)

    @loaded_dice([1, 1, 2, 2])
    def test_fumble_equal_threshold_true(self):
        """
        Test that a fumble occurs when half the dice are glitches and no hits.
        """

        roll = Roll(4)
        self.assertTrue(roll.fumble)

    @loaded_dice([1, 2, 2])
    def test_fumble_under_threshold_false(self):
        """
        Test that a fumble does not occur when under half the dice are glitches
        and there are no hits.
        """

        roll = Roll(3)
        self.assertFalse(roll.fumble)

    @loaded_dice([1, 1, 2])
    def test_fumble_over_threshold_true(self):
        """
        Test that a fumble occurs when over half of the dice are glitches and
        there are no hits.
        """

        roll = Roll(3)
        self.assertTrue(roll.fumble)

    @loaded_dice([1, 1, 5, 2])
    def test_fumble_equal_threshold_hits_false(self):
        """
        Test that a fumble does not occur when half of the dice are
        glitches but there are hits.
        """

        roll = Roll(4)
        self.assertFalse(roll.fumble)

    @loaded_dice([1, 1, 5, 1])
    def test_fumble_over_threshold_hits_false(self):
        """
        Test that a fumble does not occur when over half of the dice are
        glitches but there are hits.
        """

        roll = Roll(4)
        self.assertFalse(roll.fumble)


    @loaded_dice([1, 1, 2, 2])
    def test_fumble_glitch_true(self):
        """
        Test that a fumble is also a glitch.
        """

        roll = Roll(4)
        self.assertTrue(roll.fumble)
        self.assertTrue(roll.glitch)

    @raises(ValueError)
    def test_add_not_int_valueerror(self):
        """
        Test that adding a non-integer number of dice raises a ValueError.
        """

        roll = Roll(3)
        roll.add([2, 4, 3])

    @raises(ValueError)
    def test_add_negative_valueerror(self):
        """
        Test that adding a negative number of dice raises a ValueError.
        """

        roll = Roll(3)
        roll.add(-3)

    @raises(ValueError)
    def test_add_zero_valueerror(self):
        """
        Test that adding 0 number of dice raises a ValueError.
        """

        roll = Roll(3)
        roll.add(0)

    @loaded_dice([1, 3, 5, 2, 4, 1])
    def test_add_dice_updated(self):
        """
        Test that adding dice updates the dice list.
        """

        roll = Roll(3)
        self.assertEquals(roll.dice, [1, 3, 5])
        roll.add(3)
        self.assertEquals(roll.dice, [1, 3, 5, 2, 4, 1])

    @loaded_dice([1, 3, 5, 2, 5, 1])
    def test_add_hits_increased(self):
        """
        Test that adding dice updates the number of hits.
        """

        roll = Roll(3)
        self.assertEquals(roll.hits, 1)
        roll.add(3)
        self.assertEquals(roll.hits, 2)

    @loaded_dice([1, 2, 3, 4, 5, 1, 2, 3])
    def test_add_dice_pool_increased(self):
        """
        Test that adding dice updates the number of dice.
        """

        roll = Roll(4)
        self.assertEquals(roll.dice_pool, 4)
        roll.add(3)
        self.assertEquals(roll.dice_pool, 7)

    @loaded_dice([1, 2, 3, 4, 5, 1, 2, 3])
    def test_add_original_dice_pool_not_increased(self):
        """
        Test that adding dice does not affect the original number of dice.
        """

        roll = Roll(4)
        self.assertEquals(roll.original_dice_pool, 4)
        roll.add(3)
        self.assertEquals(roll.original_dice_pool, 4)

    @loaded_dice([1, 3, 1, 2, 5, 1])
    def test_add_gliches_added(self):
        """
        Test that adding dice updates the number of glitches.
        """

        roll = Roll(3)
        self.assertEquals(roll.glitches, 2)
        roll.add(3)
        self.assertEquals(roll.glitches, 3)

    @loaded_dice([1, 2, 5, 1, 1])
    def test_add_becomes_glitch(self):
        """
        Test that adding dice with glitches causes the roll to become a glitch.
        """

        roll = Roll(3)
        self.assertFalse(roll.glitch)
        roll.add(2)
        self.assertTrue(roll.glitch)

    @loaded_dice([1, 2, 3, 1, 1])
    def test_add_becomes_fumble(self):
        """
        Test that adding dice with glitches causes the roll to become a fumble.
        """

        roll = Roll(3)
        self.assertFalse(roll.fumble)
        roll.add(2)
        self.assertTrue(roll.fumble)

    @loaded_dice([6, 2, 3, 6, 1, 4, 1, 2])
    def test_add_edge_explodes(self):
        """
        Test that adding sixees explode, as they are added using Edge.
        """

        roll = Roll(3)
        self.assertEquals(roll.dice_pool, 3)
        roll.add(3)
        self.assertEquals(roll.dice_pool, 7)
        self.assertEquals(roll.dice, [6, 2, 3, 6, 1, 4, 1])

    @loaded_dice([1, 2, 5])
    def test_str_baseline(self):
        """
        Test that dice and hits are part of the string repesentation.
        """

        roll = Roll(3)
        self.assertTrue(str([1, 2, 5]) in str(roll))
        self.assertTrue("Hits: %d" % 1 in str(roll))

    @loaded_dice([1, 1, 5])
    def test_str_glitch(self):
        """
        Test that a glitch is part of the string representation.
        """

        roll = Roll(3)
        self.assertTrue("Glitch!" in str(roll))

    @loaded_dice([1, 1, 2])
    def test_str_fumble(self):
        """
        Test that a fumble is part of the string representation, eclipsing
        the glitch.
        """

        roll = Roll(3)
        self.assertFalse("Glitch!" in str(roll))
        self.assertTrue("Critical glitch!" in str(roll))
