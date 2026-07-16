from pathlib import Path
import re
import unittest


BACKEND = Path(__file__).resolve().parents[1]


def _requirements(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _normalized_name(requirement: str) -> str:
    name = re.split(r"(?:\[|==)", requirement, maxsplit=1)[0]
    return re.sub(r"[-_.]+", "-", name).lower()


class DependencyLockTests(unittest.TestCase):
    def test_all_dependency_versions_are_exactly_locked(self):
        direct = _requirements(BACKEND / "requirements.in")
        locked = _requirements(BACKEND / "requirements.txt")

        self.assertTrue(direct)
        self.assertTrue(locked)
        self.assertTrue(all("==" in requirement for requirement in direct))
        self.assertTrue(all("==" in requirement for requirement in locked))

    def test_lock_contains_every_direct_dependency_at_the_same_version(self):
        direct = _requirements(BACKEND / "requirements.in")
        locked = _requirements(BACKEND / "requirements.txt")
        locked_by_name = {
            _normalized_name(requirement): requirement.split("==", 1)[1]
            for requirement in locked
        }

        for requirement in direct:
            name_and_extra, version = requirement.split("==", 1)
            self.assertEqual(
                locked_by_name.get(_normalized_name(name_and_extra)),
                version,
                requirement,
            )


if __name__ == "__main__":
    unittest.main()
