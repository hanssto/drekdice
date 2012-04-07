import random
import math


class Roll(object):
    """
    A roll of a dice pool of dice, following Shadowrun rules.

    Fives and sixes are hits. Ones are glitches. A roll is a glitch if
    half or more dice are ones, or a fumble: A glitch and no hits.

    A roll can be done spending Edge. If so, 6s "explode". A hit is counted,
    and the die is rolled again, adding to the result. This is repeated for
    as long as a six is rolled.

    A die roll is immutable, but may be re-rolled and additional dice may be
    added. Added dice are always Edge dice.

    Note that this class knows nothing about success or critical success.
    That depends on a Test and a threshold.
    """

    def __init__(self, dice_pool, edge=False):
        """
        Roll a number of dice.

        Arguments:
        dice_pool -- Number of dice to roll.
        edge -- Whether to use Edge, causing sixes to explode. Default: False.
        """

        self._original_dice_pool = dice_pool
        self._dice = self._roll(dice_pool, edge)
        self._dice_pool = len(self._dice)
        self._hits = None
        self._glitches = None

    def _roll(self, dice_pool, edge=False):
        """
        Return a list of random dice rolls.

        Arguments:
        dice_pool -- Number of dice to roll.
        edge -- Whether to use Edge, causing sixes to explode. Default: False.
        """

        if type(dice_pool) != int or dice_pool < 1:
            raise ValueError("Invalid size of dice pool ", dice_pool)

        dice = []

        for i in range(dice_pool):
            roll = random.randrange(1, 7)
            dice.append(roll)
            if roll == 6 and edge:
                while roll == 6: # Rule of Six, rolled sixes "explode"
                    roll = random.randrange(1, 6)
                    dice.append(roll)

        return dice

    @property
    def dice_pool(self):
        """
        Total number dice in this roll.
        """

        if self._dice_pool == None:
            self._dice_pool = len(self._dice)
        return self._dice_pool

    @property
    def original_dice_pool(self):
        """
        Number of dice rolled in this roll, before explosions or additions.
        """

        return self._original_dice_pool

    @property
    def dice(self):
        """
        List of dice results in this roll.
        """

        return self._dice

    @property
    def hits(self):
        """
        Number of hits in this roll, fives or sixes.
        """

        if self._hits is None:
            self._hits = len([d for d in self._dice if d > 4])
        return self._hits

    @property
    def glitches(self):
        """
        Number of glitches in this roll, ones.
        """

        if self._glitches is None:
            self._glitches = len([d for d in self._dice if d == 1])
        return self._glitches

    @property
    def glitch(self):
        """
        A glitch occurs when half or more of the dice rolled are 1.
        """

        return self.glitches >= float(self.dice_pool) / 2

    @property
    def fumble(self):
        """
        A critical glitch occurs when a glitch is rolled, but no hits.
        """

        return self.glitch and not self.hits

    def add(self, dice_pool):
        """
        Roll an additional number dice and add to this roll.

        Added dice are always Edge dice so sixes explode.

        Args:
        dice_pool -- Number of dice to add.
        """

        self._dice += self._roll(dice_pool, edge=True)

        self._dice_pool = None
        self._hits = None
        self._glitches = None

    def reroll(self):
        """
        Reroll any dice that did not score a hit.

        This typically costs one point of Edge.
        """

        hits = [i for i in self._dice if i > 4]
        reroll_pool = self.dice_pool - self.hits

        if reroll_pool > 0:
            self._dice = hits + self._roll(reroll_pool)

            self._hits = None
            self._glitches = None

    def __str__(self):

        obj_str = "Roll: %s - Hits: %d" % (self.dice, self.hits)

        if self.fumble:
            obj_str += " Critical glitch!"
        elif self.glitch:
            obj_str += " Glitch!"

        return obj_str
