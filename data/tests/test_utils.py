import datetime as dt

import pytest
from data import utils
from data.models import Download, Region


@pytest.mark.django_db
def test_check_dtp(mocker):
    mocker.patch.object(utils, "check_dates_from_gibdd", autospec=True)
    mock_regions_crawl = mocker.patch.object(utils, "regions_crawl", autospec=True)

    region = Region.objects.create(level=1)
    Download.objects.create(
        region=region, date=dt.datetime.utcnow()
    )
    utils.check_dtp()

    assert mock_regions_crawl.called is True
