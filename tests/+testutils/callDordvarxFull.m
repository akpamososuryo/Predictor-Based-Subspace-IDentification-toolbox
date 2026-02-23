function [S, X, VARX, U, Zps] = callDordvarxFull(u, y, f, p, reg, opt, weight, noD)
%callDordvarxFull Call dordvarx and always return [S, X, VARX, U, Zps].
% 
% Tries common signatures so tests stay stable if optional args change.

if nargin < 5, reg = []; end
if nargin < 6, opt = []; end
if nargin < 7, weight = []; end
if nargin < 8, noD = []; end

% Try simplest
try
    [S, X, VARX, U, Zps] = dordvarx(u, y, f, p);
    return
catch
end

% Try extended signatures
candidates = {
    @() dordvarx(u, y, f, p, reg, opt, weight, noD)
    @() dordvarx(u, y, f, p, reg, opt, weight)
    @() dordvarx(u, y, f, p, reg, opt)
    @() dordvarx(u, y, f, p, reg)
};

lastErr = [];
for i = 1:numel(candidates)
    try
        [S, X, VARX, U, Zps] = candidates{i}();
        return
    catch ME
        lastErr = ME;
    end
end

rethrow(lastErr);
end