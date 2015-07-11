import unittest
from gamevariables import COLOR_TEAM_BLUE, COLOR_TEAM_RED, FIELD_LENGTH
from pitchObjects.ball import Ball
from pitchObjects.fieldplayer import FieldPlayer
from team import Team


__author__ = 'Thomas'

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.team1 = Team(True, COLOR_TEAM_BLUE, "Blue Team")
        self.team2 = Team(False, COLOR_TEAM_RED, "Red Team")
        self.ball = Ball()
        #first number is team num, second is player number
        self.player11 = FieldPlayer(1, self.team1, self.ball, 30, 30)
        self.player12 = FieldPlayer(2, self.team1, self.ball, 70, 30)
        self.player21 = FieldPlayer(1, self.team2, self.ball, 50, 30)
        self.player13 = FieldPlayer(3, self.team1, self.ball, 50, 50)
        self.ball.posX = 30
        self.ball.posY = 30
        self.ball.possessor = self.player11
        #TODO: Make it so I don't have to do this twice everywhere
        self.player11.hasBall = True
        self.team1.hasPossession = True

    def tearDown(self):
        pass

    def test_getDistanceToGoalline(self):

        #distance to left goalline should be player's posX
        self.assertEquals(self.player11.getDistanceToGoalline(False), self.player11.posX)

        self.assertEquals(self.player21.getDistanceToGoalline(True), self.player21.posX)

        #distance between goallines should be field length
        self.assertEquals(self.player11.getDistanceToGoalline(True) + self.player11.getDistanceToGoalline(False), FIELD_LENGTH)

        self.assertEquals(self.player21.getDistanceToGoalline(True) + self.player21.getDistanceToGoalline(False), FIELD_LENGTH)



if __name__ == '__main__':
    unittest.main()