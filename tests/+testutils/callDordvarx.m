function [S, X] = callDordvarx(u, y, f, p, reg, opt)
%callDordvarx  Call dordvarx with multiple signature fallbacks.
%
% Some versions of the toolbox accept extra arguments for regularization.
% This helper tries a few common patterns and returns [S, X].

if nargin < 5
    reg = [];
end
if nargin < 6
    opt = [];
end

% Always try the simplest signature first
try
    [S, X] = dordvarx(u, y, f, p);
    return
catch
end

% If no reg requested, rethrow the last error by trying again without catch
if isempty(reg)
    [S, X] = dordvarx(u, y, f, p);
    return
end

% Try common extended signatures
candidates = {
    {@() dordvarx(u, y, f, p, reg, opt)}
    {@() dordvarx(u, y, f, p, reg)}
    {@() dordvarx(u, y, f, p, reg, opt, [])}
    {@() dordvarx(u, y, f, p, reg, opt, [], 0)}
    {@() dordvarx(u, y, f, p, reg, opt, [], 1)}
};

lastErr = [];
for i = 1:numel(candidates)
    try
        [S, X] = candidates{i}{1}();
        return
    catch ME
        lastErr = ME;
    end
end

rethrow(lastErr);
end