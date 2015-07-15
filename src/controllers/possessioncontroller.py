__author__ = 'Thomas'

class PossessionController:
    """class to handle changes in possession on the team model"""
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

    def noPossession(self):
        self.team1.hasPossession = False
        self.team2.hasPossession = False

    def setPossession(self, team):
        assert (team is self.team1) or (team is self.team2)
        if team is self.team1:
            self.team1.hasPossession = True
            self.team2.hasPossession = False
        else:
            self.team2.hasPossession = True
            self.team1.hasPossession = False

    def switchPossession(self, ball):
        if self.team1.hasPossession:
            self.setPossession(self.team2)
        elif self.team2.hasPossession:
            self.setPossession(self.team1)
        else:
            assert ball.possessor is None
            self.setPossession(ball.prevPossessor.team)
            self.switchPossession(ball)

    def getTeamWithPossession(self):
        assert not (self.team1.hasPossession and self.team2.hasPossession)
        if self.team1.hasPossession:
            return self.team1
        elif self.team2.hasPossession:
            return self.team2
        else:
            return None