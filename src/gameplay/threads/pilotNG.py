from time import sleep, time
import traceback
import sys
from src.gameplay.cavebot import resolveCavebotTasks, shouldAskForCavebotTasks
from src.gameplay.combo import comboSpells
from src.gameplay.core.middlewares.battleList import setBattleListMiddleware
from src.gameplay.core.middlewares.chat import setChatTabsMiddleware
from src.gameplay.core.middlewares.gameWindow import setDirectionMiddleware, setGameWindowCreaturesMiddleware, setGameWindowMiddleware, setHandleLootMiddleware
from src.gameplay.core.middlewares.playerStatus import setMapPlayerStatusMiddleware
from src.gameplay.core.middlewares.statsBar import setMapStatsBarMiddleware
from src.gameplay.core.middlewares.radar import setRadarMiddleware, setWaypointIndexMiddleware
from src.gameplay.core.middlewares.screenshot import setScreenshotMiddleware
from src.gameplay.core.middlewares.tasks import setCleanUpTasksMiddleware
from src.gameplay.core.tasks.lootCorpse import LootCorpseTask
from src.gameplay.resolvers import resolveTasksByWaypoint
from src.gameplay.healing.observers.eatFood import eatFood
from src.gameplay.healing.observers.autoHur import autoHur
from src.gameplay.healing.observers.clearPoison import clearPoison
from src.gameplay.healing.observers.healingBySpells import healingBySpells
from src.gameplay.healing.observers.healingByPotions import healingByPotions
from src.gameplay.healing.observers.healingByMana import healingByMana
from src.gameplay.healing.observers.swapAmulet import swapAmulet
from src.gameplay.healing.observers.swapRing import swapRing
from src.gameplay.targeting import hasCreaturesToAttack
from src.repositories.gameWindow.creatures import getClosestCreature, getTargetCreature

class PilotNGThread:
    # TODO: add typings
    def __init__(self, context):
        self.context = context

    def mainloop(self):
        while True:
            try:
                if self.context.context['ng_pause']:
                    sleep(1)
                    continue
                startTime = time()
                self.context.context = self.handleGameData(
                    self.context.context)
                self.context.context = self.handleGameplayTasks(
                    self.context.context)
                self.context.context = self.context.context['ng_tasksOrchestrator'].do(
                    self.context.context)
                self.context.context['ng_radar']['lastCoordinateVisited'] = self.context.context['ng_radar']['coordinate']
                healingByPotions(self.context.context)
                healingByMana(self.context.context)
                healingBySpells(self.context.context)
                comboSpells(self.context.context)
                swapAmulet(self.context.context)
                swapRing(self.context.context)
                clearPoison(self.context.context)
                autoHur(self.context.context)
                eatFood(self.context.context)
                endTime = time()
                diff = endTime - startTime
                sleep(max(0.045 - diff, 0))
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(f"An exception occurred: {e}")
                print(traceback.format_exc())

    def handleGameData(self, context):
        if context['ng_pause']:
            return context
        context = setScreenshotMiddleware(context)
        context = setRadarMiddleware(context)
        context = setChatTabsMiddleware(context)
        context = setBattleListMiddleware(context)
        context = setGameWindowMiddleware(context)
        context = setDirectionMiddleware(context)
        context = setGameWindowCreaturesMiddleware(context)
        if context['ng_cave']['enabled'] and context['ng_cave']['runToCreatures'] == True:
            context = setHandleLootMiddleware(context)          
        else:
            context['ng_cave']['targetCreature'] = getTargetCreature(context['gameWindow']['monsters'])
        context = setWaypointIndexMiddleware(context)
        context = setMapPlayerStatusMiddleware(context)
        context = setMapStatsBarMiddleware(context)
        context = setCleanUpTasksMiddleware(context)
        return context

    def handleGameplayTasks(self, context):
        # TODO: func to check if coord is none
        if context['ng_radar']['coordinate'] is None:
            return context
        if any(coord is None for coord in context['ng_radar']['coordinate']):
            return context
        context['ng_cave']['closestCreature'] = getClosestCreature(
            context['gameWindow']['monsters'], context['ng_radar']['coordinate'])
        currentTask = context['ng_tasksOrchestrator'].getCurrentTask(context)
        if currentTask is not None and currentTask.name == 'selectChatTab':
            return context
        if len(context['loot']['corpsesToLoot']) > 0 and context['ng_cave']['runToCreatures'] == True and context['ng_cave']['enabled']:
            context['way'] = 'lootCorpses'
            if currentTask is not None and currentTask.rootTask is not None and currentTask.rootTask.name != 'lootCorpse':
                context['ng_tasksOrchestrator'].setRootTask(context, None)
            if context['ng_tasksOrchestrator'].getCurrentTask(context) is None:
                # TODO: get closest dead corpse
                firstDeadCorpse = context['loot']['corpsesToLoot'][0]
                context['ng_tasksOrchestrator'].setRootTask(
                    context, LootCorpseTask(firstDeadCorpse))
            context['gameWindow']['previousMonsters'] = context['gameWindow']['monsters']
            return context
        if context['ng_cave']['runToCreatures'] == True and context['ng_cave']['enabled']:
            hasCreaturesToAttackAfterCheck = hasCreaturesToAttack(context)
            if hasCreaturesToAttackAfterCheck:
                if context['ng_cave']['closestCreature'] is not None:
                    context['way'] = 'ng_cave'
                else:
                    context['way'] = 'waypoint'
            else:
                context['way'] = 'waypoint'
            if hasCreaturesToAttackAfterCheck and shouldAskForCavebotTasks(context):
                currentRootTask = currentTask.rootTask if currentTask is not None else None
                isTryingToAttackClosestCreature = currentRootTask is not None and (
                    currentRootTask.name == 'attackClosestCreature')
                if not isTryingToAttackClosestCreature:
                    context = resolveCavebotTasks(context)
            elif context['way'] == 'waypoint':
                if context['ng_tasksOrchestrator'].getCurrentTask(context) is None:
                    currentWaypointIndex = context['ng_cave']['waypoints']['currentIndex']
                    currentWaypoint = context['ng_cave']['waypoints']['items'][currentWaypointIndex]
                    context['ng_tasksOrchestrator'].setRootTask(
                        context, resolveTasksByWaypoint(currentWaypoint))
        elif context['ng_cave']['enabled'] and context['ng_tasksOrchestrator'].getCurrentTask(context) is None:
                currentWaypointIndex = context['ng_cave']['waypoints']['currentIndex']
                if currentWaypointIndex is not None:
                    currentWaypoint = context['ng_cave']['waypoints']['items'][currentWaypointIndex]
                    context['ng_tasksOrchestrator'].setRootTask(
                        context, resolveTasksByWaypoint(currentWaypoint))

        context['gameWindow']['previousMonsters'] = context['gameWindow']['monsters']
        return context
