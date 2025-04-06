import unittest
import datetime
from driver import DatabaseDriver, connection_params, User, RideOffer, RideRequest, RideMatch

class TestDatabaseDriver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseDriver(connection_params)
        cls.db.reset()
        cls.db.init_tables()

    @classmethod
    def tearDownClass(cls):
        cls.db.reset()
        cls.db.close()

    def test_user_crud(self):
        # Create user
        user = self.db.create_user(
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@example.com",
            phone_number="9876543210",
            is_verified=False
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "Alice")

        # Retrieve user
        fetched = self.db.get_user(user.id)
        self.assertEqual(fetched.email, "alice.smith@example.com")

        # Update user
        self.db.update_user(user.id, first_name="Alicia", is_verified=True)
        updated = self.db.get_user(user.id)
        self.assertEqual(updated.first_name, "Alicia")
        self.assertTrue(updated.is_verified)

        # Delete user
        self.db.delete_user(user.id)
        deleted = self.db.get_user(user.id)
        self.assertIsNone(deleted)

    def test_ride_offer_crud(self):
        # Create a driver user first
        driver = self.db.create_user(
            first_name="Bob",
            last_name="Driver",
            email="bob.driver@example.com",
            phone_number="1112223333",
            is_verified=True
        )
        departure_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create ride offer
        ride_offer = self.db.create_ride_offer(
            driver_id=driver.id,
            origin="CityA",
            destination="CityB",
            departure_time=departure_time,
            available_seats=3,
            description="Morning commute"
        )
        self.assertIsNotNone(ride_offer)
        self.assertEqual(ride_offer.origin, "CityA")

        # Retrieve ride offer
        fetched = self.db.get_ride_offer(ride_offer.id)
        self.assertEqual(fetched.destination, "CityB")

        # Update ride offer
        self.db.update_ride_offer(ride_offer.id, available_seats=2, description="Updated description")
        updated = self.db.get_ride_offer(ride_offer.id)
        self.assertEqual(updated.available_seats, 2)
        self.assertEqual(updated.description, "Updated description")

        # Delete ride offer
        self.db.delete_ride_offer(ride_offer.id)
        deleted = self.db.get_ride_offer(ride_offer.id)
        self.assertIsNone(deleted)

        # Clean up driver
        self.db.delete_user(driver.id)

    def test_ride_request_crud(self):
        # Create a rider user first
        rider = self.db.create_user(
            first_name="Charlie",
            last_name="Rider",
            email="charlie.rider@example.com",
            phone_number="4445556666",
            is_verified=True
        )
        departure_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create ride request
        ride_request = self.db.create_ride_request(
            rider_id=rider.id,
            origin="CityX",
            destination="CityY",
            departure_time=departure_time
        )
        self.assertIsNotNone(ride_request)
        self.assertEqual(ride_request.origin, "CityX")

        # Retrieve ride request
        fetched = self.db.get_ride_request(ride_request.id)
        self.assertEqual(fetched.destination, "CityY")

        # Update ride request
        self.db.update_ride_request(ride_request.id, destination="CityZ")
        updated = self.db.get_ride_request(ride_request.id)
        self.assertEqual(updated.destination, "CityZ")

        # Delete ride request
        self.db.delete_ride_request(ride_request.id)
        deleted = self.db.get_ride_request(ride_request.id)
        self.assertIsNone(deleted)

        # Clean up rider
        self.db.delete_user(rider.id)

    def test_ride_match_crud(self):
        # Create driver and rider
        driver = self.db.create_user(
            first_name="Diana",
            last_name="Driver",
            email="diana.driver@example.com",
            phone_number="7778889999",
            is_verified=True
        )
        rider = self.db.create_user(
            first_name="Evan",
            last_name="Rider",
            email="evan.rider@example.com",
            phone_number="0001112222",
            is_verified=True
        )
        departure_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create ride offer and ride request
        ride_offer = self.db.create_ride_offer(
            driver_id=driver.id,
            origin="TownA",
            destination="TownB",
            departure_time=departure_time,
            available_seats=4,
            description="Evening ride"
        )
        ride_request = self.db.create_ride_request(
            rider_id=rider.id,
            origin="TownA",
            destination="TownB",
            departure_time=departure_time
        )

        # Create ride match
        ride_match = self.db.create_ride_match(
            ride_offer_id=ride_offer.id,
            ride_request_id=ride_request.id,
            pending=True,
            confirmed=False
        )
        self.assertIsNotNone(ride_match)
        self.assertTrue(ride_match.pending)

        # Retrieve ride match
        fetched = self.db.get_ride_match(ride_match.id)
        self.assertEqual(fetched.ride_offer_id, ride_offer.id)

        # Update ride match
        self.db.update_ride_match(ride_match.id, pending=False, confirmed=True)
        updated = self.db.get_ride_match(ride_match.id)
        self.assertFalse(updated.pending)
        self.assertTrue(updated.confirmed)

        # Delete ride match
        self.db.delete_ride_match(ride_match.id)
        deleted = self.db.get_ride_match(ride_match.id)
        self.assertIsNone(deleted)

        # Clean up ride offer, ride request, driver and rider
        self.db.delete_ride_offer(ride_offer.id)
        self.db.delete_ride_request(ride_request.id)
        self.db.delete_user(driver.id)
        self.db.delete_user(rider.id)

if __name__ == "__main__":
    unittest.main()