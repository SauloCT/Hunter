from src.gameplay.typings import Context
# import src.gameplay.utils as gameplayUtils
import src.repositories.gameWindow.slot as gameWindowSlot
from src.repositories.gameWindow.typings import Creature
import src.utils.keyboard as utilsKeyboard
from ...typings import Context
from .common.base import BaseTask


# TODO: check if something was looted or exactly count was looted
class CollectDeadCorpseTask(BaseTask):
    def __init__(self, creature: Creature):
        super().__init__()
        self.name = 'collectDeadCorpse'
        self.creature = creature

    def do(self, context: Context) -> Context:
        utilsKeyboard.keyDown('shift')
        gameWindowSlot.rightClickSlot(
            [6, 4], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [7, 4], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [8, 4], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [6, 5], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [7, 5], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [8, 5], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [6, 6], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [7, 6], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [8, 6], context['gameWindow']['coordinate'])
        utilsKeyboard.keyUp('shift')
        return context

    def onComplete(self, context: Context) -> Context:
        # TODO: por algum motivo essa funcao de pop buga, ai ele fica tentando pegar loot infinitamente
        # TODO: verificar oque esse codigo faz e a possibilidade de voltar ele, por hora eu so limpo o array
        # this is a matrix around corpse to loot, since under corpses will be collected, it will be removed by corpsesToLoot matrix
        # coordinates = [
        #     (context['ng_radar']['coordinate'][0] - 1, context['ng_radar']
        #      ['coordinate'][1] - 1, context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0], context['ng_radar']
        #      ['coordinate'][1] - 1, context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0] + 1, context['ng_radar']
        #      ['coordinate'][1] - 1, context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0] - 1, context['ng_radar']
        #      ['coordinate'][1], context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0], context['ng_radar']
        #      ['coordinate'][1], context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0] + 1, context['ng_radar']
        #      ['coordinate'][1], context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0] - 1, context['ng_radar']
        #      ['coordinate'][1] + 1, context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0], context['ng_radar']
        #      ['coordinate'][1] + 1, context['ng_radar']['coordinate'][2]),
        #     (context['ng_radar']['coordinate'][0] + 1, context['ng_radar']
        #      ['coordinate'][1] + 1, context['ng_radar']['coordinate'][2])
        # ]
        # for coordinate in coordinates:
        #     if len(context['loot']['corpsesToLoot']) == 0:
        #         break
        #     for index, corpseToLoot in enumerate(context['loot']['corpsesToLoot']):
        #         if gameplayUtils.coordinatesAreEqual(coordinate, corpseToLoot['coordinate']):
        #         context['loot']['corpsesToLoot'].pop(index)

        context['loot']['corpsesToLoot'] = []

        return context
