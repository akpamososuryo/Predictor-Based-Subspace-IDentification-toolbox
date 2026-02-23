classdef TestLtiVarx < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function dordvarxAndDmodxHaveExpectedShapes(testCase)
            [u, y, sys] = testutils.makeSisoData('N', 400, 'seed', 1, 'noiseStd', 0.02);

            f = 5;
            p = 10;

            [S, X] = dordvarx(u, y, f, p);

            % S should be a row vector of singular values
            testCase.verifyEqual(size(S, 1), 1);
            testCase.verifyGreaterThan(numel(S), 0);

            % X should have N-p columns
            testCase.verifyEqual(size(X,2), sys.N - p);

            % Sanity checks
            testCase.verifyTrue(all(isfinite(S)), 'S contains NaN/Inf');
            testCase.verifyTrue(all(isfinite(X(:))), 'X contains NaN/Inf');
            testCase.verifyGreaterThanOrEqual(min(S), 0);

            % SVD singular values should be nonincreasing (within tolerance)
            testCase.verifyTrue(all(diff(S) <= 1e-9), 'S is not increasing');

            % dmodx should truncate to n rows
            n = 1;
            x = dmodx(X, n);
            testCase.verifySize(x, [n, sys.N - p]);
            testCase.verifyTrue(all(isfinite(x(:))), 'x contains NaN/Inf');
        end
    end
end