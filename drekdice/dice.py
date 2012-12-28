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


class SuccessTest(object):
    """
    A basic success test based on a threshold.

    A test may be a success, when the number of hits equals or exceeds the
    threshold. If four or more number of hits over the threshold are scored,
    net htis, the test results in a critical success.

    The test may also be a glitch, where half of the dice rolled are ones.
    It may also be a critical glitch, where a glitch occurs, but no hits are
    scored.

    Note that a test may both be a success and a glitch at the same time.
    """

    def __init__(self, dice_pool, threshold, edge=False):
        """
        Arguments:
        dice_pool -- Number of dice to roll.
        threshold -- The number of hits to reach.
        edge -- Whether the test is performed using Edge dice. Default False.
        """

        self._threshold = threshold
        self.edge = edge
        self._roll = Roll(dice_pool, edge=self.edge)

    @property
    def threshold(self):

        return self._threshold

    @property
    def roll(self):

        return self._roll

    @property
    def hits(self):
        """
        Number of hits, fives or sixes, this test resulted in.
        """

        return self.roll.hits

    @property
    def glitch(self):
        """
        Whether this test resulted in a glitch: More than half the
        dice rolled as ones.
        """

        return self.roll.glitch

    @property
    def fumble(self):
        """
        Whether this test resulted in a critical glitch: A glitch and no hits.
        """

        return self.roll.fumble

    @property
    def success(self):
        """
        Whether the test is successfull: If number of hits are equal or higher
        than the threshold.
        """

        return self.hits >= self.threshold

    @property
    def net_hits(self):
        """
        The number of hits above the threshold generated by this test.
        """

        net_hits = self.hits - self.threshold
        return max(net_hits, 0)

    @property
    def crit(self):
        """
        Whether the test resulted in a critical success, 4 or more net hits.
        """

        return self.net_hits >= 4

    def reroll(self):
        """
        Re-roll any dice that did not score a hit in this test.
        """

        self._roll.reroll()

    def __str__(self):

        obj_str = "Threshold: %d - Total hits: %d" % (self.threshold, self.hits)

        if self.success:
            obj_str += " - Net hits: %d - " % self.net_hits
            if self.crit:
                obj_str += "Critical success!"
            else:
                obj_str += "Success!"

        return obj_str
