-- Prevent anonymous callers from invoking the SECURITY DEFINER friendship RPC.
-- The function itself enforces auth.uid() and recipient ownership; retain access
-- for authenticated users and trusted server-side operations only.
REVOKE EXECUTE ON FUNCTION public.playam_accept_friend_request_v1(uuid) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.playam_accept_friend_request_v1(uuid) TO authenticated, service_role;
