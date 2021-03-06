import pygame
from controllers.possessioncontroller import PossessionController
from controllers.scorecontroller import ScoreController
from display.displaymapper import convertFieldPosition, convertYards2Pixels, FIELD_LENGTH, FIELD_WIDTH, WINDOW_HEADER_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT
from gamevariables import COLOR_TEAM_BLUE, COLOR_TEAM_RED, COLOR_GRASS, COLOR_PAINT, PAINT_WIDTH, COLOR_HEADER
from grandobserver import GrandObserver
from pitchObjects.ball import Ball
from pitchObjects.goal import Goal
from team import Team

__author__ = 'Thomas'

class Match:
    """Handles match gameplay"""
    def __init__(self, window):
        #Main Windows
        self.window = window

        self.header = self.createHeader()
        self.headerBG = self.createHeader()

        self.pitchSurface = self.createPitchSurface()
        self.fieldBackground = self.createPitchSurface()

        self.leftGoal = Goal(True)
        self.rightGoal = Goal(False)

        #Required Initialization of required classes for Match
        self.team1 = Team(True, COLOR_TEAM_BLUE, "Blue Team", self.leftGoal)
        self.team2 = Team(False, COLOR_TEAM_RED, "Red Team", self.rightGoal)

        self.possessionController = PossessionController(self.team1, self.team2)
        self.scoreController = ScoreController(self.team1, self.team2)

        self.ball = Ball(self.possessionController, self.scoreController, self.leftGoal, self.rightGoal)

        self.grandObserver = GrandObserver(self.team1, self.team2, self.ball)

        self.ballGroup = pygame.sprite.LayeredDirty(self.ball)

        #Pygame Sprite Groups

        #PLAYERS
        self.allPlayers = pygame.sprite.LayeredDirty()
        self.team1.setStartingLineUp((4, 3, 3), self.ball, window)
        self.allPlayers.add(self.team1.players)
        self.team2.setStartingLineUp((4, 3, 3), self.ball, window)
        self.allPlayers.add(self.team2.players)

        #OBJECTS TO BE DRAWN
        self.allPitchObjects = pygame.sprite.LayeredDirty(self.allPlayers, self.ballGroup, self.leftGoal, self.rightGoal)
        self.allPitchObjects.move_to_back(self.ball)

        # For Debugging Home Position
        # for player in self.team1.players:
        #     try:
        #         self.allPitchObjects.add(player.homePosition)
        #     except AttributeError:
        #         pass

        # Match Start Time
        self.startTime = pygame.time.get_ticks()



    def playMatchTurn(self):
        """This method ought to be repeatedly called in a while loop in the class instantiated match.py"""
        #Match Logic
        self.grandObserver.analyze()
        self.allPlayers.update(self.grandObserver)
        self.ballGroup.update(self.allPlayers)

        #Handle Graphic Display
        self.allPitchObjects.draw(self.pitchSurface)
        self.allPitchObjects.clear(self.pitchSurface, self.fieldBackground)
        self.window.blit(self.pitchSurface, (0, WINDOW_HEADER_HEIGHT))
        self.window.blit(self.header, (0, 0))

        score_font = pygame.font.Font(None, 30)
        score_render = score_font.render("{0}: {1}".format(self.team1.name, self.team1.score), True, self.team1.color)
        self.window.blit(score_render, (15,25))
        score_render = score_font.render("{0}: {1}".format(self.team2.name, self.team2.score), True, self.team2.color)
        self.window.blit(score_render, (15,55))
        time_render = score_font.render("{0}:{1}".format(pygame.time.get_ticks() / 60000, pygame.time.get_ticks() / 1000 % 60), True, COLOR_PAINT)
        self.window.blit(time_render, (WINDOW_WIDTH/2-15, 40))


    def createPitchSurface(self):
        """Draws all the markings for a standard soccer field"""
        pitchSurface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - WINDOW_HEADER_HEIGHT))
        pitchSurface.fill(COLOR_GRASS)

        #Top Line
        pygame.draw.line(pitchSurface, COLOR_PAINT, convertFieldPosition(0, 0), convertFieldPosition(FIELD_LENGTH, 0), PAINT_WIDTH)

        #Bottom Line
        pygame.draw.line(pitchSurface, COLOR_PAINT, convertFieldPosition(0, FIELD_WIDTH), convertFieldPosition(FIELD_LENGTH, FIELD_WIDTH), PAINT_WIDTH)

        #Middle Line
        pygame.draw.circle(pitchSurface, COLOR_PAINT, convertFieldPosition(FIELD_LENGTH/2, FIELD_WIDTH/2), convertYards2Pixels(10), PAINT_WIDTH)
        pygame.draw.line(pitchSurface, COLOR_PAINT, convertFieldPosition(FIELD_LENGTH/2, 0), convertFieldPosition(FIELD_LENGTH/2, FIELD_WIDTH), PAINT_WIDTH)

        #LEFT SIDE
        pygame.draw.line(pitchSurface, COLOR_PAINT, convertFieldPosition(0, 0), convertFieldPosition(0, FIELD_WIDTH), PAINT_WIDTH)

        centerOfGoalLine = convertFieldPosition(0, FIELD_WIDTH/2)

        sixYardBox = pygame.Rect(centerOfGoalLine[0], (centerOfGoalLine[1] - convertYards2Pixels(10)), convertYards2Pixels(6), convertYards2Pixels(20))
        pygame.draw.rect(pitchSurface, COLOR_PAINT, sixYardBox, PAINT_WIDTH)

        plenaltyBox = pygame.Rect(centerOfGoalLine[0], (centerOfGoalLine[1] - convertYards2Pixels(22)), convertYards2Pixels(18), convertYards2Pixels(44))
        pygame.draw.rect(pitchSurface, COLOR_PAINT, plenaltyBox, PAINT_WIDTH)

        #RIGHT SIDE
        pygame.draw.line(pitchSurface, COLOR_PAINT, convertFieldPosition(FIELD_LENGTH, 0), convertFieldPosition(FIELD_LENGTH, FIELD_WIDTH), PAINT_WIDTH)

        centerOfGoalLine = convertFieldPosition(FIELD_LENGTH, FIELD_WIDTH/2)

        sixYardBox = pygame.Rect((centerOfGoalLine[0] - convertYards2Pixels(6)) , (centerOfGoalLine[1] - convertYards2Pixels(10)), convertYards2Pixels(6), convertYards2Pixels(20))
        pygame.draw.rect(pitchSurface, COLOR_PAINT, sixYardBox, PAINT_WIDTH)

        plenaltyBox = pygame.Rect((centerOfGoalLine[0] - convertYards2Pixels(18)), (centerOfGoalLine[1] - convertYards2Pixels(22)), convertYards2Pixels(18), convertYards2Pixels(44))
        pygame.draw.rect(pitchSurface, COLOR_PAINT, plenaltyBox, PAINT_WIDTH)


        return pitchSurface

    def createHeader(self):
        header = pygame.Surface((WINDOW_WIDTH, WINDOW_HEADER_HEIGHT))
        header.fill(COLOR_HEADER)

        return header
