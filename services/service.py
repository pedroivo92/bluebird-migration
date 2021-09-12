from migrator_db import MigrationRepository
from authentication import AuthRepository
from bluebird import BluebirdHandler
from globomail import GlobomailRepository
from settings import *


class IntegratorService:

    def __init__(self, logger):
        self.migration_repository = None
        self.globomail_repository = None
        self.roundcube_repository = None
        try:
            self.logger = logger
            self.migration_repository = MigrationRepository()
            self.globomail_repository = GlobomailRepository()
            self.authenticator = AuthRepository(AUTH_USER, AUTH_PASSWORD, AUTH_URL, self.logger)
            self.bluebird_handler = BluebirdHandler(self.logger)

        except Exception as e:
            self._close_connections()
            raise e

    def handler_bluebird_migration(self):
        try:
            migration_items = self.migration_repository.get_pending_migrations()
            for item in migration_items:
                self.logger.info(msg=f'starting bluebird migration for id_globo: {item["id_globo"]}')
                sucess = self._handler_bluebird_process(item)
                if not sucess:
                    continue

        finally:
            self._close_connections()

    def _get_cached_token(self, service_name):
        token_st = None

        token_tgt = self.authenticator.generate_token_tgt(service_name)
        if token_tgt:
            token_st = self.authenticator.generate_token_st(token_tgt, service_name)

        return token_st

    def _handler_bluebird_process(self, item):        
        item = dict(item)
        token_bluebird_st = self._get_cached_token(str(AUTH_SERVICE_BLUEBIRD))

        if not item['id_stage']:
            item['id_stage'] = 10 
        
        if item['id_stage'] == 12:
            sucess = self._checkout_cart(item, token_bluebird_st)
            if not sucess:
                return False
        if item['id_stage'] == 11:
            cart_id = self._create_cart(item, token_bluebird_st)
            if not cart_id:
                return False

            item['cart_id'] = cart_id
            sucess = self._checkout_cart(item, token_bluebird_st)
            if not sucess:
                return False
        else:
            sucess = self._create_payment_method(item, token_bluebird_st)
            if not sucess:
                return False

            cart_id = self._create_cart(item, token_bluebird_st)
            if not cart_id:
                return False

            item['cart_id'] = cart_id
            sucess = self._checkout_cart(item, token_bluebird_st)
            if not sucess:
                return False

        return True


    def _create_payment_method(self, item, token_bluebird_st):
        payment_method, error = self.bluebird_handler.create_payment_method(item['customer_id'], token_bluebird_st)
        if error:
            self.migration_repository.update_migration_process(item, 10, error)
            return False

        return True

    def _create_cart(self, item, token_bluebird_st):
        quota = self.globomail_repository.call_function(item['current_email_address'])
        
        plan = self.bluebird_handler.get_plan(quota['quota'])

        cart_id, error = self.bluebird_handler.create_cart(item['customer_id'], plan, token_bluebird_st)
        if error:
            self.migration_repository.update_migration_process(item, 11, error)
            return False

        self.migration_repository.update_plan_informations(item, cart_id)
        return cart_id

    def _checkout_cart(self, item, token_bluebird_st):
        payment_method, error = self.bluebird_handler.checkout_cart(item['cart_id'], token_bluebird_st)
        if error:
            self.migration_repository.update_migration_process(item, 12, error)
            return False

        return True

    def _close_connections(self):
        if self.migration_repository:
            self.migration_repository.close_connections()

        if self.globomail_repository:
            self.globomail_repository.close_connections()
