import math

import pygame

from display.displaymapper import FIELD_WIDTH, FIELD_LENGTH
from gamevariables import STRAT_BLOCKAGE, STRAT_COVERAGE, STRAT_MIN_PASS


__author__ = 'Thomas'


class GrandObserver:
    def __init__(self, team1, team2, ball):
        self.team1 = team1
        self.team2 = team2

        self.ball = ball

        self.closestDefender = None
        self.stoppingPlayer = None

    def analyze(self):
        """
        Examines the current relationships between the players and the ball. Sets flags on particular players to help
        guide their personal decisions when they are updated.
        """
        # TODO: optimize these functions to reduce repeated looping
        # I'm not actually sure how much time I am losing here, might be worth testing before refactoring everything
        if self.team1.hasPossession:
            attackingTeam = self.team1
            defendingTeam = self.team2
        else:
            attackingTeam = self.team2
            defendingTeam = self.team1

        attackingTeam.players.sort(key=lambda x: x.getDistanceToGoalline(True))
        defendingTeam.players.sort(key=lambda x: x.getDistanceToGoalline(False))

        self.lastDefender = defendingTeam.players[1]  # goalie is excluded
        self.lastAttacker = attackingTeam.players[-2]  # goalie is excluded

        self.resumePlay = True
        if self.ball.outOfPlay is "Kickoff":
            for player in attackingTeam.players:
                if attackingTeam.isDefendingLeft:
                    if player.posX > FIELD_LENGTH/2:
                        self.resumePlay = False
                elif player.posX < FIELD_WIDTH/2:
                    self.resumePlay = False
            for player in defendingTeam.players:
                if defendingTeam.isDefendingLeft:
                    if player.posX > FIELD_LENGTH/2:
                        self.resumePlay = False
                elif player.posX < FIELD_LENGTH/2:
                    self.resumePlay = False
                if player.getDistanceTo(self.ball) < 10:
                    self.resumePlay = False

        self.findClosestDefenders(defendingTeam)
        self.setCoveredAndBlockedPlayers(attackingTeam, defendingTeam)
        self.setOffsides(attackingTeam)
        self.setOpenPlayers(attackingTeam)
        self.setMarkingsAndClosestAttacker(attackingTeam, defendingTeam)

    def setMarkingsAndClosestAttacker(self, attackingTeam, defendingTeam):
        closestAttacker = attackingTeam.players[0]
        for attackingPlayer in attackingTeam.players:
            for defendingPlayer in sorted(defendingTeam.players, key=lambda x: abs(x.posX - attackingPlayer.posX) + abs(
                            x.posY - attackingPlayer.posY)):
                if not defendingPlayer.marking:
                    defendingPlayer.marking = attackingPlayer
                    break

            attackingPlayer.chargeToBall = False
            if attackingPlayer.getDistanceTo(self.ball) < closestAttacker.getDistanceTo(self.ball):
                closestAttacker = attackingPlayer

        closestAttacker.chargeToBall = True

    def findClosestDefenders(self, defendingTeam):
        if not self.closestDefender:
            self.closestDefender = defendingTeam.players[0]
        if not self.stoppingPlayer:
            self.stoppingPlayer = defendingTeam.players[0]
        previousClosestDefender = self.closestDefender
        previousStoppingPlayer = self.stoppingPlayer


        self.openPlayers = []
        for defendingPlayer in defendingTeam.players:
            defendingPlayer.blocking = []
            defendingPlayer.covering = []
            defendingPlayer.chargeToBall = False
            defendingPlayer.marking = None

            if previousClosestDefender.getDistanceTo(self.ball) - 2 > defendingPlayer.getDistanceTo(self.ball) < self.closestDefender.getDistanceTo(self.ball):
                self.closestDefender = defendingPlayer
            if defendingPlayer.getDistanceToGoalline(False) < self.ball.getDistanceToGoalline(False, defendingPlayer.team.isDefendingLeft):
                if previousStoppingPlayer.getDistanceTo(self.ball) - 2 > defendingPlayer.getDistanceTo(self.ball) < self.stoppingPlayer.getDistanceTo(self.ball):
                    self.stoppingPlayer = defendingPlayer

        self.closestDefender.chargeToBall = True
        self.stoppingPlayer.chargeToBall = True


    def setCoveredAndBlockedPlayers(self, attackingTeam, defendingTeam):
        for attackingPlayer in attackingTeam.players:
            attackingPlayer.blockedBy = []
            attackingPlayer.coveredBy = []
            for defendingPlayer in defendingTeam.players:
                # Check blocked players
                # TODO: use player attributes as modifiers
                if attackingPlayer.getDistanceTo(self.ball) > defendingPlayer.getDistanceTo(self.ball):
                    defendingAngle = math.atan2(self.ball.posX - defendingPlayer.posX,
                                                self.ball.posY - defendingPlayer.posY)
                    passingAngle = math.atan2(self.ball.posX - attackingPlayer.posX,
                                              self.ball.posY - attackingPlayer.posY)
                    angleDif = abs(((defendingAngle - passingAngle + math.pi) % (2 * math.pi)) - math.pi)
                    stratBlockage = STRAT_BLOCKAGE
                    if self.ball.possessor:
                        if defendingPlayer.getDistanceTo(self.ball) < STRAT_MIN_PASS:
                            stratBlockage = math.radians(60)
                    if angleDif < stratBlockage:
                        attackingPlayer.blockedBy += [defendingPlayer]
                        defendingPlayer.blocking += [attackingPlayer]

                # if the defending player is nearby and closer to the goal
                if (attackingPlayer.posX - defendingPlayer.posX) ** 2 + (
                            attackingPlayer.posY - defendingPlayer.posY) ** 2 < STRAT_COVERAGE:
                    attackingPlayer.coveredBy += [defendingPlayer]
                    defendingPlayer.covering += [attackingPlayer]

    def setOffsides(self, attackingTeam):
        for attackingPlayer in attackingTeam.players:
            if not self.ball.isLoose:
                attackingPlayer.isOffsides = False
                if attackingPlayer.getDistanceToGoalline(True) < FIELD_WIDTH / 2:
                    if self.attackerIsCloserToGoalline(attackingPlayer, self.lastDefender):
                        if self.ball.possessor and attackingPlayer.getDistanceToGoalline(
                                True) < self.ball.possessor.getDistanceToGoalline(True):
                            attackingPlayer.isOffsides = True
                        elif not self.ball.possessor:
                            attackingPlayer.isOffsides = True

    def setOpenPlayers(self, attackingTeam):
        for attackingPlayer in attackingTeam.players:
            if not attackingPlayer.isOffsides and not attackingPlayer.coveredBy and not attackingPlayer.blockedBy:
                self.openPlayers.append(attackingPlayer)

    def attackerIsCloserToGoalline(self, attacker, defender):
        if attacker.getDistanceToGoalline(True) < \
                defender.getDistanceToGoalline(False):
            return True
        else:
            return False