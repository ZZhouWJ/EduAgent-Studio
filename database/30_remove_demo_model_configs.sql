-- Remove seeded credentials and mock models from product-facing model governance.
USE `ai_collab_audit_system`;

UPDATE api_configs ac
INNER JOIN model_providers provider
  ON provider.provider_id = ac.provider_id
SET ac.status = 'disabled',
    ac.is_deleted = 1,
    ac.deleted_at = COALESCE(ac.deleted_at, NOW()),
    ac.updated_at = NOW()
WHERE ac.is_deleted = 0
  AND (
    provider.provider_code = 'mock'
    OR ac.key_mask IN ('sk-****test', 'sk-****dsk')
  );

UPDATE ai_models model
INNER JOIN model_providers provider
  ON provider.provider_id = model.provider_id
SET model.status = 'disabled',
    model.is_deleted = 1,
    model.deleted_at = COALESCE(model.deleted_at, NOW()),
    model.updated_at = NOW()
WHERE model.is_deleted = 0
  AND provider.provider_code = 'mock';

UPDATE model_providers
SET status = 'disabled',
    is_deleted = 1,
    deleted_at = COALESCE(deleted_at, NOW()),
    updated_at = NOW()
WHERE provider_code = 'mock'
  AND is_deleted = 0;
