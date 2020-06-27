import datetime as dt

import pytest
from data import utils
from data.models import Download, Region


@pytest.mark.parametrize("tags", [True, False])
@pytest.mark.django_db
def test_check_dtp(mocker, tags):
    mocker.patch.object(utils, "check_dates_from_gibdd", autospec=True)
    mock_crawl = mocker.patch.object(utils, "crawl", autospec=True)

    region = Region.objects.create(level=1)
    Download.objects.create(
        region=region, base_data=False, date=dt.datetime.utcnow(), tags=False
    )
    Download.objects.create(
        region=region, base_data=True, date=dt.datetime.utcnow(), tags=False
    )

    utils.check_dtp(tags=tags)

    assert mock_crawl.called is True
