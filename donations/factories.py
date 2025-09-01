import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Импортируйте ваши модели
from .models import (
    Level, Contact, Currency, CurrencyPriceHistory,
    Subscription, Donation, Goal
)


class LevelFactory(DjangoModelFactory):
    class Meta:
        model = Level

    name = factory.Sequence(lambda n: f'Level {n}')
    description = factory.Faker('paragraph', nb_sentences=3)


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency
        django_get_or_create = ('code',)  # Избегает дублирования по коду

    name = factory.Sequence(lambda n: f'Currency {n}')
    code = factory.Sequence(lambda n: f'CUR{n}')


class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    telegram = factory.Faker('user_name')
    phone = factory.Faker('phone_number', locale='ru_RU')
    status = Contact.Status.ACTIVE


class GoalFactory(DjangoModelFactory):
    class Meta:
        model = Goal

    target_amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    start_date = factory.Faker('past_date', start_date='-1y')
    
    # Гарантирует, что end_date всегда будет после start_date
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=90))


class CurrencyPriceHistoryFactory(DjangoModelFactory):
    class Meta:
        model = CurrencyPriceHistory

    currency = factory.SubFactory(CurrencyFactory)
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    datetime = factory.Faker('past_datetime', tzinfo=timezone.get_current_timezone())


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription

    contact = factory.SubFactory(ContactFactory)
    level = factory.SubFactory(LevelFactory)
    amount = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    currency = factory.SubFactory(CurrencyFactory)
    frequency = Subscription.Frequency.MONTHLY
    start_date = factory.Faker('past_date', start_date='-6m')
    end_date = None  # По умолчанию подписка бессрочная
    source = "Test Factory"

    class Params:
        # Трейт для активной подписки
        active = factory.Trait(
            start_date=factory.Faker('past_date', start_date='-1y'),
            end_date=None
        )
        # Трейт для неактивной (закончившейся) подписки
        inactive = factory.Trait(
            start_date=factory.Faker('past_date', start_date='-2y'),
            end_date=factory.Faker('past_date', start_date='-1y')
        )
        # Трейт для подписки, которая начнется в будущем
        future = factory.Trait(
            start_date=factory.Faker('future_date', end_date='+1y'),
            end_date=None
        )


class DonationFactory(DjangoModelFactory):
    class Meta:
        model = Donation

    # Поля по умолчанию для анонимного, неподтвержденного пожертвования
    contact = None
    subscription = None
    amount = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    currency = factory.SubFactory(CurrencyFactory)
    amount_in_base_currency = None
    donation_datetime = factory.Faker('past_datetime', tzinfo=timezone.get_current_timezone())
    source = "Test Factory"
    is_confirmed = False

    class Params:
        # Трейт для пожертвования, связанного с подпиской
        from_subscription = factory.Trait(
            subscription=factory.SubFactory(SubscriptionFactory),
            # Автоматически устанавливает контакт из связанной подписки
            contact=factory.LazyAttribute(lambda o: o.subscription.contact)
        )
        # Трейт для пожертвования от контакта (без подписки)
        with_contact = factory.Trait(
            contact=factory.SubFactory(ContactFactory),
            subscription=None
        )
        # Трейт для подтвержденного пожертвования
        confirmed = factory.Trait(
            is_confirmed=True,
            # Устанавливает сумму в базовой валюте (для простоты равна основной)
            amount_in_base_currency=factory.LazyAttribute(lambda o: o.amount)
        )
