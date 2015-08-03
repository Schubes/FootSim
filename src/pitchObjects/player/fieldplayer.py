import math

import pygame

from display.displaymapper import FIELD_LENGTH, FIELD_WIDTH
from gamevariables import STRAT_NEAR_BALL, ATTR_PLAYER_SPEED, ATTR_SHOOTING_RANGE, GRAPH_PLAYER_SIZE, ATTR_PLAYER_ACCEL, \
    STRAT_MIN_PASS, STRAT_TRY_CROSSING, STRAT_NEIGHBOR_MIN_DISTANCE
from pitchObjects.player.abstractPlayer import AbstractPlayer
from pitchObjects.homeposition import HomePosition
from pitchObjects.pitchobject import PitchObject


__author__ = 'Thomas'

class FieldPlayer(AbstractPlayer):
    """Class for players currently on the pitch"""

    def __init__(self, playerRole, team, ball, posX, posY):
        """
        playerRole is a tuple (giving the percent position)
        """

        AbstractPlayer.__init__(self, team.color, posX, posY, GRAPH_PLAYER_SIZE)

        self.homePosition = HomePosition(playerRole, team, ball)

        self.playerRole = playerRole
        self.team = team
        self.ball = ball

    def update(self, grandObserver):
        """ This nethod is called by matchturn using existing pygame.sprite implementation"""
        self.homePosition.update()
        self.makeAction(grandObserver)
        AbstractPlayer.update(self)

    def makeAction(self, grandObserver):
        """
        Calls the appropriate action logic for the player based on possession and ball control status.
        """
        if self.team.hasPossession:
            if self.hasBall:
                self.makePlay(grandObserver)
            elif (self.ball.possessor is None) and self.chargeToBall:
                self.chase(self.ball)
            else:
                self.makeRun(grandObserver)
        else:
            self.defend()

    def makePlay(self, grandObserver):
        """
        Logic for the player who possesses the ball
        """
        if self.ball.outOfPlay:
            self.mustPass()
        elif self.isInShootingRange():
            self.ball.shoot(self.team.isDefendingLeft)
        else:
            if not self.lookToPass(grandObserver):
                if self.getDistanceToGoalline(True) < STRAT_TRY_CROSSING:
                    self.mustPass()
                self.makeRun(grandObserver)

    def makeRun(self, grandObserver):
        """ handles and prioritizes all offensive movement"""
        # During Kickoffs, don't move
        if self.ball.outOfPlay is "Kickoff":
            pass

        # If about to go offsides run back onsides
        elif grandObserver.lastDefender.getDistanceToGoalline(False) > self.getDistanceToGoalline(True) \
                < self.ball.getDistanceToGoalline(True, self.team.isDefendingLeft) and \
                        self.getDistanceToGoalline(True) < FIELD_LENGTH/2:
            self.accelerate( -self.dirX(1), 0)
            return

        else:
            #If the player is the intended recipient of a pass try to receive it
            if self.ball.target is self:
                self.intercept(self.ball)
                return
            #If the player has the ball, move towards the goal, or if that is blocked, move towards open space
            elif self.hasBall:
                if pygame.sprite.collide_rect(self, self.homePosition):
                    if grandObserver.stoppingPlayer.getDistanceTo(self) < STRAT_NEAR_BALL:
                        # run along a right angle to the defender
                        if self.team.isDefendingLeft:
                            if grandObserver.stoppingPlayer.posX - self.posX < 0:
                                print "oops"
                        self.accelerate(grandObserver.stoppingPlayer.posX - self.posX, grandObserver.stoppingPlayer.posY - self.posY)
                        return
                    else:
                        self.accelerate(1,0)
                        return
            elif pygame.sprite.collide_rect(self, self.homePosition):
                if self.ball.possessor:
                    if abs(self.posY - FIELD_WIDTH/2) - abs(self.ball.possessor.posY - FIELD_WIDTH/2) > 0:
                        self.chase(self.homePosition)
                        return
                    self.cover(self.ball.possessor)
                    return

            else:
                self.chase(self.homePosition)
                return


    def defend(self):
        """ handles and prioritizes all defensive movement"""
        if self.ball.outOfPlay:
            self.chase(self.homePosition)
            return
        if self.chargeToBall or self.nearBall() and ((self.ball.posX - self.posX) < 0 == self.ball.velX < 0) and \
                ((self.ball.posY - self.posY) < 0 == self.ball.velY < 0):
            if self.cover(self.ball):
                self.chase(self.ball)
            return
        if not pygame.sprite.collide_rect(self, self.homePosition):
            self.chase(self.homePosition)
            return
        if self.marking:
            self.cover(self.marking)
            return

        self.team.players.sort(key=lambda x: x.getDistanceTo(self))
        ind = 0
        neighbor = self.team.players[ind]
        while neighbor.getDistanceTo(self) < STRAT_NEIGHBOR_MIN_DISTANCE:
            # if neighbor.getDistanceTo(self.homePosition) < self.getDistanceTo(self.homePosition) \
            #         and neighbor.getDistanceTo(neighbor.homePosition) > self.getDistanceTo(neighbor.homePosition):
            #     print "Position swap"
            #     newPosition = neighbor.homePosition
            #     neighbor.homePosition = self.homePosition
            #     self.homePosition = newPosition
            if neighbor.getDistanceTo(self.ball) < self.getDistanceTo(self.ball):
                if neighbor.getDistanceTo(neighbor.homePosition) > self.getDistanceTo(neighbor.homePosition):
                    self.cover(neighbor.homePosition)
                return

            ind += 1
            if ind >= len(self.team.players):
                break
            neighbor = self.team.players[ind]

        else:
            self.cover(self.ball)
            return