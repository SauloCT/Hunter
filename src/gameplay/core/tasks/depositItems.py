from src.repositories.inventory.core import images
from src.shared.typings import Waypoint
from ...typings import Context
from .common.vector import VectorTask
from .closeContainer import CloseContainerTask
from .dragItems import DragItemsTask
from .dropBackpackIntoStash import DropBackpackIntoStashTask
from .goToFreeDepot import GoToFreeDepotTask
from .openBackpack import OpenBackpackTask
from .openDepot import OpenDepotTask
from .openLocker import OpenLockerTask
from .scrollToItem import ScrollToItemTask
from .setNextWaypoint import SetNextWaypointTask
from .expandBackpack import ExpandBackpackTask

class DepositItemsTask(VectorTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'depositItems'
        self.delayBeforeStart = 1
        self.delayAfterComplete = 1
        self.isRootTask = True
        self.waypoint = waypoint

    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
            GoToFreeDepotTask(self.waypoint).setParentTask(self).setRootTask(self),
            OpenLockerTask().setParentTask(self).setRootTask(self),
            OpenBackpackTask(context['ng_backpacks']['main']).setParentTask(self).setRootTask(self),
            ExpandBackpackTask(context['ng_backpacks']['main']).setParentTask(self).setRootTask(self),
            ScrollToItemTask(images['containersBars'][context['ng_backpacks']['main']], images['slots'][context['ng_backpacks']['loot']]).setParentTask(self).setRootTask(self),
            DropBackpackIntoStashTask(context['ng_backpacks']['loot']).setParentTask(self).setRootTask(self),
            OpenDepotTask().setParentTask(self).setRootTask(self),
            OpenBackpackTask(context['ng_backpacks']['loot']).setParentTask(self).setRootTask(self),
            DragItemsTask(images['containersBars'][context['ng_backpacks']['loot']], images['slots']['depot chest 2']).setParentTask(self).setRootTask(self),
            CloseContainerTask(images['containersBars'][context['ng_backpacks']['loot']]).setParentTask(self).setRootTask(self),
            SetNextWaypointTask().setParentTask(self).setRootTask(self),
        ]
        return context
