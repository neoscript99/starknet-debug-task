from functools import reduce
import os
import pytest
from inspect import signature
from starkware.starknet.testing.starknet import Starknet
from asynctest import TestCase
from starkware.starknet.compiler.compile import compile_starknet_files

# The path to the contract source code.
CONTRACT_FILE = os.path.join("contracts", "array_contract.cairo")
PRODUCT_ARRAY = [(x, x + 1) for x in range(1, 6, 2)]

print(reduce(lambda x, y: x * y, list(sum(PRODUCT_ARRAY, ()))))

class CairoContractTest(TestCase):
    @classmethod
    async def setUp(cls):
        cls.starknet = await Starknet.empty()

        compiled_contract = compile_starknet_files(
            [CONTRACT_FILE], debug_info=True, disable_hint_validation=True
        )
        kwargs = (
            {"contract_def": compiled_contract}
            if "contract_def" in signature(cls.starknet.deploy).parameters
            else {"contract_class": compiled_contract}
        )
        cls.contract = await cls.starknet.deploy(**kwargs)

    @pytest.mark.asyncio
    async def test_array_contract(self):
        res = await self.contract.view_product(array=PRODUCT_ARRAY).call()
        self.assertEqual(
            res.call_info.result.pop(),
            self.contract.contract_address
            + reduce(lambda x, y: x * y, list(sum(PRODUCT_ARRAY, ()))),
            "Contract is still not correct",
        )
