import pygame
from display.displaymapper import FIELD_LENGTH, FIELD_WIDTH
from gamevariables import STRAT_HOME_POS_SIZE, COLOR_ORANGE
from pitchObjects.pitchobject import PitchObject

__author__ = 'Thomas'

class HomePosition(PitchObject):
    def __init__(self, playerRole, team, ball):
        self.team = team
        self.ball = ball

        self.perX = playerRole[0]
        self.perY = playerRole[1]

        self.defaultPosX = (self.relX(self.perX * FIELD_LENGTH/2, self.team.isDefendingLeft))
        self.defaultPosY = self.perY * FIELD_WIDTH

        PitchObject.__init__(self, COLOR_ORANGE, self.defaultPosX, self.defaultPosY, STRAT_HOME_POS_SIZE)

    def update(self):
        self.posX = self.defaultPosX + self.ballModifierX() + self.attackingModifierX()
        self.posY = self.defaultPosY + self.ballModifierY() + self.defendingModifierY()
        PitchObject.update(self)

    def ballModifierX(self):
        #TODO: use time * transistionspeed
        return (self.ball.posX - FIELD_LENGTH/2)/10

    def ballModifierY(self):
        balltracking = (self.ball.posY - FIELD_WIDTH/2) * 2/3 * abs(self.defaultPosY - self.ball.posY)/FIELD_WIDTH
        if self.posX < 30:
            overloadingBox = (FIELD_WIDTH/2 - self.defaultPosY)/(50/(30-self.posX))
        elif self.posX > 90:
            overloadingBox = (FIELD_WIDTH/2 - self.defaultPosY)/(50/(self.posX-90))
        else:
            if self.posX > FIELD_LENGTH/2:
                overloadingBox = (FIELD_WIDTH/2 - self.defaultPosY)/(100/(self.posX + 1 - FIELD_LENGTH))/2
            else:
                overloadingBox = (FIELD_WIDTH/2 - self.defaultPosY)/(100/(self.posX + 1))/2
        return balltracking + overloadingBox

    def defendingModifierY(self):
        if not self.team.hasPossession:
            return (self.ball.posY - self.defaultPosY)/FIELD_WIDTH
        else:
            return 0

    def attackingModifierX(self):
        if self.team.hasPossession:
            setPieceMultiplier = 1
            if self.ball.outOfPlay is "GoalKick" or self.ball.outOfPlay is "CornerKick":
                setPieceMultiplier = 2
            if self.team.isDefendingLeft:
                return self.defaultPosX * setPieceMultiplier
            else:
                return (self.defaultPosX - FIELD_LENGTH) * setPieceMultiplier
        else:
            return 0