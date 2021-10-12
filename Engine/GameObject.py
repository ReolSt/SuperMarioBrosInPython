import pico2d

from .Singleton import *
from .Settings import *
from .Transform import *

class GameObjectIDGenerator(metaclass=Singleton):
    OBJECT_MAX_ID = int(Settings().default["GameObjectMaxId"])
    def __init__(self):
        """

        Returns
        -------
        None.

        """

        self.currentId = 0

    def generate(self):
        """
        Returns
        -------
        generated_id : int
            DESCRIPTION.

        """

        generated_id = self.currentId

        self.currentId = (self.currentId + 1) % GameObjectIDGenerator.OBJECT_MAX_ID
        return generated_id

class GameObject:
    def __init__(self, parent=None):
        """
        Parameters
        ----------
        parent : GameObject or Transform, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """

        if isinstance(parent, GameObject):
            self.transform = Transform(parent.transform, self)
        else:
            self.transform = Transform(parent, self)

        self.id = GameObjectIDGenerator().generate()

        self.children = []
        self.sprites = []

        self.eventListeners = {
            "Update": [],
            "Render": [],
            "MouseMove": [],
            "MouseDown": [],
            "MouseUp": [],
            "MouseWheel": [],
            "KeyDown": [],
            "KeyPress": [],
            "KeyUp": [],
            "CollisionEnter": [],
            "CollisionStay": [],
        }

        self.keyDown = {}

        self.layer = "Default"

        if self.transform.parent is not None:
            self.scene = self.transform.parent.gameObject.scene

        self.colliders = []

    def captureEvent(self, event):
        """
        Parameters
        ----------
        event : SDL_Event
            DESCRIPTION.

        Returns
        -------
        None.

        """

        if event.type == pico2d.SDL_MOUSEBUTTONUP:
            event.y = int(Settings().default["WindowHeight"]) - 1 - event.y
            self.onMouseUp(event)
        elif event.type == pico2d.SDL_MOUSEBUTTONDOWN:
            event.y = int(Settings().default["WindowHeight"]) - 1 - event.y
            self.onMouseDown(event)
        elif event.type == pico2d.SDL_MOUSEMOTION:
            event.y = int(Settings().default["WindowHeight"]) - 1 - event.y
            self.onMouseMove(event)
        elif event.type == pico2d.SDL_MOUSEWHEEL:
            event.y = int(Settings().default["WindowHeight"]) - 1 - event.y
            self.onMouseWheel(event)
        elif event.type == pico2d.SDL_KEYDOWN:
            if event.key is None:
                for key in self.keyDown:
                    if self.keyDown[key]:
                        event.key = key
                        self.onKeyPress(event)
            elif event.key not in self.keyDown:
                self.keyDown[event.key] = False

            if not self.keyDown[event.key]:
                self.onKeyDown(event)
                self.keyDown[event.key] = True
        elif event.type == pico2d.SDL_KEYUP:
            if event.key == None:
                return

            if event.key not in self.keyDown:
                self.keyDown[event.key] = False
            self.keyDown[event.key] = False

            self.onKeyUp(event)

    def addEventListener(self, eventType, callback):
        """
        Parameters
        ----------
        eventType : str
            DESCRIPTION.
        callback : function
            DESCRIPTION.

        Returns
        -------
        None.

        """

        assert(eventType in self.eventListeners.keys())

        self.eventListener[eventType].append(callback)

    def removeEventListeners(self, eventType):
        """
        Parameters
        ----------
        eventType : str
            DESCRIPTION.

        Returns
        -------
        None.

        """

        assert(eventType in self.eventListeners.keys())

        self.eventListeners[eventType] = []

    def update(self, deltaTime):
        """

        Parameters
        ----------
        deltaTime : float
            DESCRIPTION.

        Returns
        -------
        None.

        """

        for callback in self.eventListeners["Update"]:
            callback(self)

        for child in self.children:
            child.update(deltaTime)

    def render(self, camera, debug=False):
        for callback in self.eventListeners["Render"]:
            callback(self)

        if camera.layer == self.layer:
            for sprite in self.sprites:
                sprite.render(camera)

            if debug:
                for collider in self.colliders:
                    collider.render(camera)

        for child in self.children:
            child.render(camera, debug)

    def onMouseMove(self, event):
        for callback in self.eventListeners["MouseMove"]:
            callback(self, event)

        for child in self.children:
            child.onMouseMove(event)

    def onMouseDown(self, event):
        for callback in self.eventListeners["MouseDown"]:
            callback(self, event)

        for child in self.children:
            child.onMouseDown(event)

    def onMouseUp(self, event):
        for callback in self.eventListeners["MouseUp"]:
            callback(self, event)

        for child in self.children:
            child.onMouseUp(event)

    def onMouseWheel(self, event):
        for callback in self.eventListeners["MouseWheel"]:
            callback(self, event)

        for child in self.children:
            child.onMouseWheel(event)

    def onKeyDown(self, event):
        for callback in self.eventListeners["KeyDown"]:
            callback(self, event)

        for child in self.children:
            child.onKeyDown(event)

    def onKeyUp(self, event):
        for callback in self.eventListeners["KeyUp"]:
            callback(self, event)

        for child in self.children:
            child.onKeyUp(event)

    def onKeyPress(self, event):
        for callback in self.eventListeners["KeyPress"]:
            callback(self, event)

        for child in self.children:
            child.onKeyPress(event)

    def onCollisionEnter(self, collision):
        pass

    def onCollisionStay(self, collision):
        pass

    def onCollisionExit(self, collision):
        pass

    def addCollider(self, collider):
        assert hasattr(self, "scene"), "addCollider : object has no scene property."

        self.colliders.append(collider)
        self.scene.collisionManager.addCollider(collider)

    def removeCollider(self, collider):
        assert hasattr(self, "scene"), "removeCollider : object has no scene property."

        self.colliders.remove(collider)
        self.scene.collisionManager.removeCollider(collider)