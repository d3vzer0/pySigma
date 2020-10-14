import pytest
from datetime import date
from uuid import UUID
from sigma.rule import SigmaRuleTag, SigmaLogSource, SigmaDetectionItem, SigmaDetection, SigmaDetections, SigmaStatus, SigmaLevel, SigmaRule, SigmaError

### SigmaRuleTag tests ###
def test_sigmaruletag_fromstr():
    assert SigmaRuleTag.from_str("namespace.name") == SigmaRuleTag("namespace", "name")

def test_sigmaruletag_fromstr_nodot():
    with pytest.raises(ValueError):
        SigmaRuleTag.from_str("tag")

def test_sigmaruletag_fromstr_3dots():
    assert SigmaRuleTag.from_str("namespace.subnamespace.tag") == SigmaRuleTag("namespace", "subnamespace.tag")

### SigmaLogSource tests ###

def test_sigmalogsource_fromdict():
    logsource = SigmaLogSource.from_dict({
        "category": "category-id",
        "product": "product-id",
        "service": "service-id",
        })
    assert logsource == SigmaLogSource("category-id", "product-id", "service-id")

def test_sigmalogsource_fromdict_no_category():
    logsource = SigmaLogSource.from_dict({
        "product": "product-id",
        "service": "service-id",
        })
    assert logsource == SigmaLogSource(None, "product-id", "service-id")

def test_sigmalogsource_fromdict_no_product():
    logsource = SigmaLogSource.from_dict({
        "category": "category-id",
        "service": "service-id",
        })
    assert logsource == SigmaLogSource("category-id", None, "service-id")

def test_sigmalogsource_fromdict_no_service():
    logsource = SigmaLogSource.from_dict({
        "category": "category-id",
        "product": "product-id",
        })
    assert logsource == SigmaLogSource("category-id", "product-id", None)

def test_sigmalogsource_empty():
    with pytest.raises(SigmaError):
        SigmaLogSource(None, None, None)

# SigmaDetectionItem
def test_sigmadetectionitem_keyword_single():
    """Single keyword detection."""
    assert SigmaDetectionItem.from_mapping(None, "value") == SigmaDetectionItem(None, [], ["value"])

def test_sigmadetectionitem_keyword_list():
    """Keyword list detection."""
    assert SigmaDetectionItem.from_mapping(None, ["value1", "value2"]) == SigmaDetectionItem(None, [], ["value1", "value2"])

def test_sigmadetectionitem_keyword_modifiers():
    """Keyword detection with modifier chain."""
    assert SigmaDetectionItem.from_mapping("|mod1|mod2", "value") == SigmaDetectionItem(None, ["mod1", "mod2"], ["value"])

def test_sigmadetectionitem_key_value_single():
    """Key-value detection with one value."""
    assert SigmaDetectionItem.from_mapping("key", "value") == SigmaDetectionItem("key", [], ["value"])

def test_sigmadetectionitem_key_value_list():
    """Key-value detection with value list."""
    assert SigmaDetectionItem.from_mapping("key", ["value1", "value2"]) == SigmaDetectionItem("key", [], ["value1", "value2"])

def test_sigmadetectionitem_key_value_modifiers():
    """Key-value detection with modifier chain."""
    assert SigmaDetectionItem.from_mapping("key|mod1|mod2", "value") == SigmaDetectionItem("key", ["mod1", "mod2"], ["value"])

def test_sigmadetectionitem_fromvalue():
    SigmaDetectionItem.from_value("test") == SigmaDetectionItem(None, [], "test")

### SigmaDetections tests ###

def test_sigmadetections_fromdict():
    detections = {
        "keyword_list": [
            "keyword_1",
            "keyword_2",
            "keyword_3",
            ],
        "test_list_of_maps": [
                {
                    "key1": "value1"
                },
                {
                    "key2": "value2"
                },
            ],
        "test_map": {
                "key1": "value1",
                "key2": "value2",
            },
        }
    condition = "1 of them"
    sigma_detections = SigmaDetections.from_dict({
        **detections,
        "condition": condition,
        })
    assert sigma_detections == SigmaDetections(
            detections = {
                "keyword_list": SigmaDetection([
                    SigmaDetectionItem(None, [], [ "keyword_1" ]),
                    SigmaDetectionItem(None, [], [ "keyword_2" ]),
                    SigmaDetectionItem(None, [], [ "keyword_3" ]),
                ]),
                "test_list_of_maps": SigmaDetection([
                    SigmaDetection([SigmaDetectionItem("key1", [], [ "value1" ])]),
                    SigmaDetection([SigmaDetectionItem("key2", [], [ "value2" ])]),
                ]),
                "test_map": SigmaDetection([
                    SigmaDetectionItem("key1", [], [ "value1" ]),
                    SigmaDetectionItem("key2", [], [ "value2" ]),
                ])
            },
            condition = [ condition ],
            )

def test_sigmadetections_fromdict_no_detections():
    with pytest.raises(SigmaError):
        SigmaDetections.from_dict({ "condition": "selection" })

def test_sigmadetections_fromdict_no_condition():
    with pytest.raises(SigmaError):
        SigmaDetections.from_dict({ "selection": { "key": "value" }})

### SigmaRule tests ###

def test_sigmarule_bad_uuid():
    with pytest.raises(SigmaError):
        SigmaRule.from_dict({ "id": "no-uuid" })

def test_sigmarule_bad_level():
    with pytest.raises(SigmaError):
        SigmaRule.from_dict({ "level": "bad" })

def test_sigmarule_bad_status():
    with pytest.raises(SigmaError):
        SigmaRule.from_dict({ "status": "bad" })

def test_sigmarule_bad_date():
    with pytest.raises(SigmaError):
        SigmaRule.from_dict({ "date": "bad" })

def test_sigmarule_no_logsource():
    with pytest.raises(SigmaError):
        SigmaRule.from_dict({})

def test_sigmarule_no_detections():
    with pytest.raises(SigmaError):
        SigmaRule.from_dict({ "logsource": { "category": "category-id" } })

def test_sigmarule_fromyaml():
    sigmarule_from_yaml = SigmaRule.from_yaml("""
    title: Test
    id: 9a6cafa7-1481-4e64-89a1-1f69ed08618c
    status: test
    description: This is a test
    references:
        - ref1
        - ref2
    tags:
        - attack.execution
        - attack.t1059
    author: Thomas Patzke
    date: 2020/07/12
    logsource:
        category: process_creation
        product: windows
    detection:
        selection_1:
            CommandLine|contains: test.exe
        selection_2:
            - CommandLine|contains: test.exe
            - CommandLine|contains: cmd.exe
        selection_3:
            - keyword_1
            - keyword_2
        condition: 1 of them
    fields:
        - User
        - CommandLine
    falsepositives:
        - Everything
    level: low
    """)
    sigmarule = SigmaRule(
        title = "Test",
        id = UUID("9a6cafa7-1481-4e64-89a1-1f69ed08618c"),
        status = SigmaStatus["test"],
        description = "This is a test",
        references = [
            "ref1",
            "ref2",
        ],
        tags = [
            SigmaRuleTag.from_str("attack.execution"),
            SigmaRuleTag.from_str("attack.t1059"),
        ],
        author = "Thomas Patzke",
        date = date(2020, 7, 12),
        logsource = SigmaLogSource(
            category = "process_creation",
            product = "windows",
            service = None,
        ),
        detection = SigmaDetections(
            detections = {
                "selection_1": SigmaDetection([
                        SigmaDetectionItem("CommandLine", ["contains"], [ "test.exe" ])
                    ]),
                "selection_2": SigmaDetection([
                        SigmaDetection([SigmaDetectionItem("CommandLine", ["contains"], [ "test.exe" ])]),
                        SigmaDetection([SigmaDetectionItem("CommandLine", ["contains"], [ "cmd.exe" ])]),
                    ]),
                "selection_3": SigmaDetection([
                    SigmaDetectionItem(None, [], [ "keyword_1" ]),
                    SigmaDetectionItem(None, [], [ "keyword_2" ]),
                ]),
            },
            condition = [ "1 of them" ],
        ),
        fields = [
            "User",
            "CommandLine",
        ],
        falsepositives = [
            "Everything",
        ],
        level = SigmaLevel["low"],
    )
    assert sigmarule_from_yaml == sigmarule
