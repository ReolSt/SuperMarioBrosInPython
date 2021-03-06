import pico2d

from Engine.Vector2 import Vector2
from Engine.GameObject import GameObject
from Engine.EntitySprite import EntitySprite
from Engine.RigidBody import RigidBody
from Engine.AudioMixer import AudioMixer

import pymunk

import os
if os.path.dirname(os.path.abspath(__file__)) == os.getcwd():
    from .ColliderCategories import *
else:
    from Entities.ColliderCategories import *

class Goomba(GameObject):
    def __init__(self, parent, colorType=1, direction=1):
        super().__init__(parent)

        self.animationSprites = {
            "Walk1": EntitySprite(self, "Goomba" + str(colorType) + "Walk1"),
            "Walk2": EntitySprite(self, "Goomba" + str(colorType) + "Walk2"),
            "Die": EntitySprite(self, "Goomba" + str(colorType) + "Dead"),
        }

        self.sprites = [self.animationSprites["Walk1"]]

        self.removeReady = False

        self.died = False
        self.dieAnimationTimeStep = 0

        self.epsilon = 0.01

        self.velocity = Vector2(200 * direction, 0)

        self.runAnimationFrame = 1
        self.runAnimationInterval = 20000
        self.runAnimationFrameDuration = 0

        self.removeRemainedTime = 1000

        for spriteName in self.animationSprites:
            width = self.animationSprites[spriteName].width
            height = self.animationSprites[spriteName].height
            self.animationSprites[spriteName].transform.localPosition = Vector2(width / 2, height / 2)

        self.width = self.sprites[0].width
        self.height = self.sprites[0].height

        self.rigidBody = RigidBody(self)
        self.rigidBody.vertices = [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)]
        self.rigidBody.bodyType = "Dynamic"
        self.rigidBody.filter = GOOMBA_CATEGORY
        self.rigidBody.mass = 1000
        self.rigidBody.moment = float('inf')
        self.rigidBody.elasticity = 0

        self.switchSprite("Walk1")

        self.player = None

    def switchSprite(self, spriteName):
        self.sprites[0] = self.animationSprites[spriteName]

        self.width = self.sprites[0].width
        self.height = self.sprites[0].height

        self.vertices = [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)]

    def updateAnimation(self, deltaTime):
        if self.died:
            self.switchSprite("Die")
            return

        self.switchSprite("Walk" + str(self.runAnimationFrame))

        self.runAnimationFrameDuration += deltaTime * abs(self.rigidBody.velocityX)

        if self.runAnimationFrameDuration > self.runAnimationInterval:
            self.runAnimationFrame = (self.runAnimationFrame % 2) + 1
            self.runAnimationFrameDuration = 0.0

    def changeDirection(self):
        bb = self.rigidBody.bb
                
        centerX = (bb.left + bb.right) / 2
        centerY = (bb.bottom + bb.top) / 2
        for queryInfo in self.rigidBody.space.shape_query(self.rigidBody.shape):
            shape = queryInfo.shape
            contactPoints = queryInfo.contact_point_set.points
            if shape.filter.categories & 0b1:
                for contactPoint in contactPoints:
                    point_a = contactPoint.point_a
                    point_b = contactPoint.point_b
                    if point_a.y < centerY:
                        continue
                    if bb.left - 1 <= point_a.x <= bb.left + 1:
                        self.velocity.x = -self.velocity.x
                        return
                    if bb.right - 1 <= point_a.x <= bb.right + 1:
                        self.velocity.x = -self.velocity.x
                        return

    def updateDie(self, deltaTime):
        if self.died:
            return

        bb = self.rigidBody.bb
                
        for queryInfo in self.rigidBody.space.shape_query(self.rigidBody.shape):
            shape = queryInfo.shape
            contactPoints = queryInfo.contact_point_set.points
            if shape.filter.categories & PLAYER_CATEGORY:
                for contactPoint in contactPoints:
                    point_a = contactPoint.point_a
                    point_b = contactPoint.point_b
                    if bb.left + 2 <= point_a.x <= bb.right - 2 and bb.top - 2 <= point_a.y < bb.top + 2:
                        self.died = True
                        self.rigidBody = None

                        shape.body.velocity = shape.body.velocity.x, 300

                        AudioMixer().playWav("Stomp")

    def updateMovement(self, deltaTime):
        if self.died:
            return

        self.changeDirection()

        self.rigidBody.velocityX = self.velocity.x
    
    def update(self, deltaTime):
        super().update(deltaTime)

        if self.player is None:
            return

        if abs(self.player.transform.getPosition().x - self.transform.getPosition().x) > 600:
            return

        self.updateAnimation(deltaTime)

        self.updateDie(deltaTime)
        self.updateMovement(deltaTime)

        if self.died:
            if self.removeRemainedTime <= 0:
                self.removeReady = True
            else:
                self.removeRemainedTime -= deltaTime
            return

        self.rigidBody.angle = 0