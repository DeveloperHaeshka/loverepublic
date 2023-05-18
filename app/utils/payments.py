import random

from dataclasses import dataclass

from anypay import AnyPayAPI, Bill


@dataclass
class CheckResponse:

    is_paid: bool
    amount: int = 0


@dataclass
class DummyBill:

    id: int
    url: str = 'https://google.com'


class BasePayment(object):

    async def check_payment(self, payment_id: int) -> CheckResponse:

        return CheckResponse(True, 1)

    async def create_payment(self, amount: int) -> DummyBill:

        return DummyBill(
            id=random.getrandbits(32),
        )


class AnyPay(BasePayment):

    def __init__(self, api_id: str, api_key: str, project_id: int, project_secret: str):

        self.api = AnyPayAPI(api_id, api_key, project_id, project_secret)

    async def create_payment(self, amount: int) -> Bill:

        return await self.api.create_bill(
            pay_id=random.getrandbits(32),
            amount=amount,
        )

    async def check_payment(self, payment_id: int) -> CheckResponse:

        bills = await self.api.get_payments(pay_id=payment_id)

        if not bills:

            return CheckResponse(False)

        return CheckResponse(
            bills[0].status == 'paid',
            bills[0].amount,
        )
