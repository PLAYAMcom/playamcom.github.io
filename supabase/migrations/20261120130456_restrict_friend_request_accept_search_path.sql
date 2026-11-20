-- The function references application objects with explicit schemas.
-- An empty search_path prevents objects in writable schemas shadowing names.
ALTER FUNCTION public.playam_accept_friend_request_v1(uuid) SET search_path = '';
