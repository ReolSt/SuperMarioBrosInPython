from Engine.Singleton import Singleton
from Engine.Settings import Settings
from Engine.Scene import Scene
from Engine.GameObject import GameObject

from Level import Level

from Objects.Background import Background
from Objects.Ground import Ground
from Objects.Mountain import Mountain
from Objects.Block import Block
from Objects.MysteryBlock import MysteryBlock
from Objects.Brick import Brick
from Objects.VerticalPipe import VerticalPipe
from Objects.HorizontalPipe import HorizontalPipe
from Objects.Cloud import Cloud
from Objects.Grass import Grass
from Objects.Tree import Tree
from Objects.Mushroom import Mushroom
from Objects.Flagpole import Flagpole

from Entities.Goomba import Goomba

class LevelLoader(metaclass=Singleton):
    def __init__(self):
        self.levelFilePath = Settings().level["LevelFilePath"]

    def load(self, parent, fileName):
        filePath = self.levelFilePath + fileName + ".txt"

        level = Level(parent)

        objects = GameObject(level)
        entities = GameObject(level)

        level.addChildren([objects, entities])
        
        level.objects = objects.children
        level.entities = entities.children

        parserState = "Player"

        with open(filePath, "r") as file:
            i = 0
            for line in file.readlines():
                tokens = line.split()

                if parserState == "Player":
                    assert len(tokens) == 2
                    x, y = map(int, tokens)
                    level.playerInitialPosition.x = x
                    level.playerInitialPosition.y = y

                    parserState = "BGM"
                    continue

                elif parserState == "BGM":
                    if len(tokens) == 0:
                        level.bgm = ""
                    else:
                        assert len(tokens) == 1
                        bgm = tokens[0]
                        level.bgm = bgm

                        parserState = "Background"
                        continue

                elif parserState == "Background":
                    assert len(tokens) == 1
                    spriteName = str(tokens[0])

                    gameObject = Background(level, 800, 600, spriteName)
                    gameObject.layer = "Background"
                    level.addChild(gameObject)                    

                    parserState = "GameObject"
                    continue

                if len(tokens) == 0:
                    continue

                assert 5 <= len(tokens) <= 7

                objectName, x, y, width, height = tokens[:5]
                x, y, width, height = int(x), int(y), int(width), int(height)

                if len(tokens) >= 6:
                    colorType = int(tokens[5])

                if len(tokens) >= 7:
                    direction = int(tokens[6])

                gameObject = None

                if objectName == "Ground":
                    gameObject = Ground(level, width, height, colorType)
                elif objectName == "Mountain":
                    gameObject = Mountain(level, height)
                elif objectName == "Block":
                    gameObject = Block(level, width, height, colorType)
                elif objectName == "MysteryBlock":
                    gameObject = MysteryBlock(level, colorType)
                elif objectName == "Brick":
                    gameObject = Brick(level, width, height, colorType)
                elif objectName == "VerticalPipe":
                    gameObject = VerticalPipe(level, height)
                elif objectName == "HorizontalPipe":
                    gameObject = HorizontalPipe(level, width, height)
                elif objectName == "Cloud":
                    gameObject = Cloud(level, width)
                elif objectName == "Grass":
                    gameObject = Grass(level, width)
                elif objectName == "Tree":
                    gameObject = Tree(level, height)
                elif objectName == "Mushroom":
                    gameObject = Mushroom(level, width, height)
                elif objectName == "Flagpole":
                    gameObject = Flagpole(level, height)
                elif objectName == "Goomba":
                    gameObject = Goomba(level, colorType, direction)

                if gameObject is not None:
                    level.setGridPosition(gameObject, x, y)

                    if objectName in ["Goomba"]:
                        entities.addChild(gameObject)
                    else:
                        objects.addChild(gameObject)

        return level